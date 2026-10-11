"""UART stimulus and capture timing, handshake, overflow, and reset checks."""
import random

import cocotb
from cocotb.triggers import Timer
from model.events import Event, capture_events


async def tick(dut, **inputs):
    # Drive with clock low; inspect before and after the sampling edge.
    dut.clk.value = 0
    for name, value in inputs.items():
        getattr(dut, name).value = value
    await Timer(5, unit="ns")
    transferred = read_event(dut) if int(dut.rst_n.value) and int(dut.event_valid.value) and int(dut.event_ready.value) else None
    dut.clk.value = 1
    await Timer(5, unit="ns")
    return transferred


def read_event(dut):
    return Event(int(dut.event_delta.value), int(dut.event_mask.value), int(dut.event_value.value))


async def reset(dut):
    await tick(dut, rst_n=0, start=0, stop=0, pins=1, event_ready=1)
    assert not int(dut.event_valid.value)
    assert not int(dut.active.value)
    assert not int(dut.overflow.value)
    await tick(dut, rst_n=1)


async def begin(dut, pins=1):
    await tick(dut, start=1, pins=pins)
    assert int(dut.initial_value.value) == pins
    # Deassert without advancing a cycle; the next tick is sample cycle 1.
    dut.start.value = 0


async def check_samples(dut, samples, initial=1):
    await reset(dut)
    await begin(dut, initial)
    observed = []
    for value in samples:
        event = await tick(dut, pins=value)
        if event is not None:
            observed.append(event)
    event = await tick(dut, stop=1)
    if event is not None:
        observed.append(event)
    assert observed == capture_events(initial, samples)
    assert not int(dut.overflow.value)


@cocotb.test()
async def uart_frame(dut):
    # UART 8N1: idle, start, 0xA5 LSB first, stop. Pin 1 stays low.
    cycles_per_bit = 8
    bits = [1, 0] + [(0xA5 >> bit) & 1 for bit in range(8)] + [1]
    samples = [bit for bit in bits for _ in range(cycles_per_bit)]
    await check_samples(dut, samples)
    dut._log.info("Captured UART 0xA5: event deltas/masks/values match cycle reference")


@cocotb.test()
async def consecutive_and_simultaneous_transitions(dut):
    await check_samples(dut, [0, 3, 1, 2, 0, 0, 3], initial=0)
    rng = random.Random(42)
    await check_samples(dut, [rng.randrange(4) for _ in range(200)])


@cocotb.test()
async def stalled_payload_and_overflow(dut):
    await reset(dut)
    await begin(dut)
    await tick(dut, pins=0, event_ready=0)
    held = read_event(dut)
    for _ in range(3):
        await tick(dut)
        assert int(dut.event_valid.value)
        assert read_event(dut) == held
    await tick(dut, pins=1)
    assert int(dut.overflow.value)
    assert not int(dut.active.value)
    assert read_event(dut) == held
    assert await tick(dut, event_ready=1) == held
    await tick(dut)
    assert not int(dut.event_valid.value)
    assert int(dut.overflow.value)
    await begin(dut)
    assert not int(dut.overflow.value)


@cocotb.test()
async def stall_then_consume_and_replace(dut):
    await reset(dut)
    await begin(dut)
    await tick(dut, pins=0, event_ready=0)
    await tick(dut)
    assert await tick(dut, pins=3, event_ready=1) == Event(1, 1, 0)
    assert read_event(dut) == Event(2, 3, 3)
    assert not int(dut.overflow.value)


@cocotb.test()
async def delta_limit_and_reset(dut):
    await check_samples(dut, [1] * 254 + [0])
    await reset(dut)
    await begin(dut)
    for _ in range(255):
        await tick(dut)
    assert int(dut.active.value)
    await tick(dut, pins=0)
    assert int(dut.overflow.value)
    assert not int(dut.active.value)
    assert not int(dut.event_valid.value)
    await reset(dut)
    await begin(dut)
    await tick(dut, pins=0, event_ready=0)
    await reset(dut)


@cocotb.test()
async def control_boundaries(dut):
    await reset(dut)
    await begin(dut)
    # Repeated start is ignored; capture still records the transition.
    await tick(dut, start=1, pins=0, event_ready=0)
    assert read_event(dut) == Event(1, 1, 0)
    assert int(dut.initial_value.value) == 1
    # Stop suppresses a simultaneous transition and retains the blocked event.
    await tick(dut, start=0, stop=1, pins=3)
    assert not int(dut.active.value)
    assert not int(dut.overflow.value)
    assert read_event(dut) == Event(1, 1, 0)
    # A pending event prevents restart, even when consumed on this edge.
    assert await tick(dut, stop=0, start=1, event_ready=1) == Event(1, 1, 0)
    assert not int(dut.active.value)
    await tick(dut, start=1)
    assert int(dut.active.value)
    assert int(dut.initial_value.value) == 3
    await tick(dut, rst_n=0, start=1, stop=1)
    assert not int(dut.active.value)
    assert not int(dut.event_valid.value)
