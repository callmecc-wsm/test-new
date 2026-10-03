/**
 * 纯逻辑计数器：取值 0–20，供浏览器与 Node 测试共用。
 */
(function (root, factory) {
  if (typeof module !== "object" || !module.exports) {
    root.CounterModel = factory();
    return;
  }
  module.exports = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const MIN = 0;
  const MAX = 20;

  /**
   * @returns {{ value: number, increment: Function, decrement: Function, reset: Function, getControls: Function }}
   */
  function createCounter(initial = MIN) {
    let value = clamp(initial);

    function clamp(n) {
      if (n < MIN) return MIN;
      if (n > MAX) return MAX;
      return n;
    }

    function getControls() {
      return {
        canIncrement: value < MAX,
        canDecrement: value > MIN,
        min: MIN,
        max: MAX,
      };
    }

    return {
      get value() {
        return value;
      },
      increment() {
        if (value < MAX) value += 1;
        return value;
      },
      decrement() {
        if (value > MIN) value -= 1;
        return value;
      },
      reset() {
        value = MIN;
        return value;
      },
      getControls,
    };
  }

  return { createCounter, MIN, MAX };
});
