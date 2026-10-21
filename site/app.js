const form = document.querySelector('#calculator-form');
const result = document.querySelector('#result');
const historyList = document.querySelector('#history');
const clearHistoryButton = document.querySelector('#clear-history');
const operationNames = {
  add: '+',
  subtract: '−',
  multiply: '×',
  divide: '÷',
  power: '^',
};

function calculate(operation, left, right) {
  if (!Number.isFinite(left) || !Number.isFinite(right)) {
    throw new Error('请输入两个有效数字。');
  }

  switch (operation) {
    case 'add': return left + right;
    case 'subtract': return left - right;
    case 'multiply': return left * right;
    case 'divide':
      if (right === 0) throw new Error('除数不能为 0。');
      return left / right;
    case 'power': return left ** right;
    default: throw new Error('请选择有效的运算方式。');
  }
}

function formatNumber(value) {
  if (!Number.isFinite(value)) return String(value);
  return new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 10 }).format(value);
}

function setResult(message, isError = false) {
  result.textContent = message;
  result.classList.toggle('is-error', isError);
}

function addHistory(entry) {
  const emptyState = historyList.querySelector('.empty-history');
  if (emptyState) emptyState.remove();

  const item = document.createElement('li');
  item.textContent = entry;
  historyList.prepend(item);
  while (historyList.children.length > 5) historyList.lastElementChild.remove();
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const left = Number(form.elements.left.value);
  const right = Number(form.elements.right.value);
  const operation = form.elements.operation.value;

  if (form.elements.left.value.trim() === '' || form.elements.right.value.trim() === '') {
    setResult('请先填写两个数字。', true);
    return;
  }

  try {
    const answer = calculate(operation, left, right);
    const expression = `${formatNumber(left)} ${operationNames[operation]} ${formatNumber(right)} = ${formatNumber(answer)}`;
    setResult(expression);
    addHistory(expression);
  } catch (error) {
    setResult(error.message, true);
  }
});

clearHistoryButton.addEventListener('click', () => {
  historyList.replaceChildren();
  const emptyState = document.createElement('li');
  emptyState.className = 'empty-history';
  emptyState.textContent = '结果会显示在这里';
  historyList.append(emptyState);
});
