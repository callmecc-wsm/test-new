import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const { createCounter, MIN, MAX } = require("./counter.js");

test("初始值为 0", () => {
  const c = createCounter();
  assert.equal(c.value, 0);
  assert.deepEqual(c.getControls(), {
    canIncrement: true,
    canDecrement: false,
    min: MIN,
    max: MAX,
  });
});

test("递增到上限 10 后不可再增", () => {
  const c = createCounter();
  for (let i = 0; i < MAX; i += 1) {
    c.increment();
  }
  assert.equal(c.value, MAX);
  assert.equal(c.getControls().canIncrement, false);
  c.increment();
  assert.equal(c.value, MAX);
});

test("递减到下限 0 后不可再减", () => {
  const c = createCounter();
  c.decrement();
  assert.equal(c.value, 0);
  assert.equal(c.getControls().canDecrement, false);
});

test("重置回到 0", () => {
  const c = createCounter();
  c.increment();
  c.increment();
  c.reset();
  assert.equal(c.value, 0);
});

test("非法初始值会被钳制到范围内", () => {
  assert.equal(createCounter(-5).value, MIN);
  assert.equal(createCounter(99).value, MAX);
});
