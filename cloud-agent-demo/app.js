/**
 * 将 CounterModel 绑定到页面控件。
 */
(function () {
  var counter = CounterModel.createCounter(0);

  var valueEl = document.getElementById("counter-value");
  var btnPlus = document.getElementById("btn-plus");
  var btnMinus = document.getElementById("btn-minus");
  var btnReset = document.getElementById("btn-reset");

  function render() {
    valueEl.textContent = String(counter.value);
    var controls = counter.getControls();
    btnPlus.disabled = !controls.canIncrement;
    btnMinus.disabled = !controls.canDecrement;
    btnReset.disabled = counter.value === 0;
  }

  btnPlus.addEventListener("click", function () {
    counter.increment();
    render();
  });

  btnMinus.addEventListener("click", function () {
    counter.decrement();
    render();
  });

  btnReset.addEventListener("click", function () {
    counter.reset();
    render();
  });

  render();
})();
