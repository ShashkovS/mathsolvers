'use strict';
let blockNum = 0;


// Initialize Ace editor
const editor = ace.edit("editor");
const langTools = ace.require("ace/ext/language_tools");
const snippetManager = ace.require("ace/snippets").snippetManager;
const Range = ace.require('ace/range').Range;

editor.setOptions({
    fontSize: "14px",
    fontFamily: "Cascadia Mono, monospace",
    enableBasicAutocompletion: false,
    enableLiveAutocompletion: true,
    enableSnippets: true,
    theme: 'ace/theme/dracula',
    mode: 'ace/mode/latex',
    wrap: true,
});
// editor.session.setUseWrapMode(true);


const aceLatexSnippets = [
    {name: "frac", content: "\\frac{${1:}}{${2:}}", score: 1000, meta: "\\frac{}{}"},
    {name: "dfrac", content: "\\dfrac{${1:}}{${2:}}", score: 100, meta: "\\dfrac{}{}"},
    {name: "дробь", content: "\\frac{${1:}}{${2:}}", score: 100, meta: "\\frac{}{}"},
    {name: "block", content: "${1:}\naction\n${2:}\nsolution\n${3:}\nanswer\n${4:}\n", score: 50, meta: "action/solution/answer"},
    {name: "блок", content: "${1:}\naction\n${2:}\nsolution\n${3:}\nanswer\n${4:}\n", score: 50, meta: "action/solution/answer"},
    {name: "answer", content: "final_answer\n${1:}", score: 50, meta: "final_answer"},
    {name: "ответ", content: "final_answer\n${1:}", score: 50, meta: "final_answer"},
    {name: "длр", content: "$ ${1: } $", score: 1000, meta: "$ $"},
    {name: "ддлр", content: "$$${1: }$$", score: 50, meta: "$$ $$"},
    {name: "solve", content: "<<solve ${1:} >>", score: 50, meta: "<<solve ...>>"},
    {name: "решить", content: "<<solve ${1:} >>", score: 50, meta: "<<solve ...>>"},
    {name: "calc", content: "<<calc ${1:} >>", score: 50, meta: "<<calc ...>>"},
    {name: "считать", content: "<<calc ${1:} >>", score: 50, meta: "<<calc ...>>"},
    {name: "simplify", content: "<<simplify ${1:} >>", score: 50, meta: "<<simplify ...>>"},
    {name: "упростить", content: "<<simplify ${1:} >>", score: 50, meta: "<<simplify ...>>"},
    {name: "factor", content: "<<factor ${1:} >>", score: 50, meta: "<<factor ...>>"},
    {name: "units", content: "<<units ${1:} >>", score: 50, meta: "<<units ...>>"},
    {name: "format", content: "<<format ${1:} >>", score: 50, meta: "<<format ...>>"},
    {name: "compare", content: "<<compare ${1:} >>", score: 50, meta: "<<compare ...>>"},
];
const latexCommands = [
    {caption: "cdot", value: "\\cdot", meta: "⋅", score: 100},
    {caption: "точка", value: "\\cdot", meta: "⋅", score: 100},
    {caption: "sqrt", value: "\\sqrt", meta: "Корень", score: 90},
    {caption: "корень", value: "\\sqrt", meta: "Корень", score: 90},
    {caption: "div", value: "\\div", meta: "÷", score: 80},
    {caption: "делить", value: "\\div", meta: "÷, \\div", score: 80},
    {caption: "approx", value: "\\approx", meta: "≈", score: 50},
    {caption: "примерно", value: "\\approx", meta: "≈", score: 50},
    {caption: "pi", value: "\\pi", meta: "𝜋", score: 50},
    {caption: "пи", value: "\\pi", meta: "𝜋", score: 50},
    {caption: "alpha", value: "\\alpha", meta: "α", score: 50},
    {caption: "альфа", value: "\\alpha", meta: "α", score: 50},
    {caption: "circ", value: "\\circ", meta: "∘", score: 50},
    {caption: "градус", value: "^\\circ", meta: "∘", score: 50},
    {caption: "le", value: "\\le", meta: "⩽", score: 60},
    {caption: "мр", value: "\\le", meta: "⩽", score: 60},
    {caption: "ме", value: "<", meta: "<", score: 60},
    {caption: "ge", value: "\\ge", meta: "⩾", score: 60},
    {caption: "бр", value: "\\ge", meta: "⩾", score: 60},
    {caption: "бо", value: ">", meta: ">", score: 60},
    {caption: "ne", value: "\\ne", meta: "≠", score: 60},
    {caption: "нер", value: "\\ne", meta: "≠", score: 60},
    {caption: "overline", value: "\\overline", meta: "Черта сверху", score: 50},
    {caption: "times", value: "\\times", meta: "×", score: 50},
    {caption: "умножить", value: "\\times", meta: "×", score: 50},
    {caption: "begin", value: "\\begin", meta: "\\begin", score: 50},
    {caption: "начать", value: "\\begin", meta: "\\begin", score: 50},
    {caption: "end", value: "\\end", meta: "\\end", score: 50},
    {caption: "закончить", value: "\\end", meta: "\\end", score: 50},
    {caption: "офс", value: "{", meta: "{", score: 1000},
    {caption: "фс", value: "{", meta: "{", score: 1000},
    {caption: "зфс", value: "}", meta: "}", score: 1000},
    {caption: "чч", value: "x", meta: "x", score: 50},
    {caption: "нн", value: "y", meta: "y", score: 50},
    {caption: "степень", value: "^", meta: "степень", score: 50},
    {caption: "модуль", value: "|", meta: "модуль", score: 50},
    {caption: "плюс-минус", value: "\\pm", meta: "±", score: 50},
    {caption: "\\pm", value: "\\pm", meta: "±", score: 50},
    {caption: "N", value: "\\mathbb{N}", meta: "ℕ", score: 50},
    {caption: "Z", value: "\\mathbb{Z}", meta: "ℤ", score: 50},
    {caption: "Q", value: "\\mathbb{Q}", meta: "ℚ", score: 50},
    {caption: "R", value: "\\mathbb{R}", meta: "ℝ", score: 50},
    {caption: "C", value: "\\mathbb{C}", meta: "ℂ", score: 50},
    {caption: "cancel", value: "\\cancel", meta: "\\cancel", score: 50},
    {caption: "bcancel", value: "\\bcancel", meta: "\\bcancel", score: 30},
    {caption: "infty", value: "\\infty", meta: "∞", score: 50},
    {caption: "in", value: "\\in", meta: "∈", score: 50},
    {caption: "ldots", value: "\\ldots", meta: "…", score: 50},
    {caption: "overline", value: "\\overline", meta: "\\overline", score: 50},
    {caption: "sin", value: "\\sin", meta: "sin", score: 40},
    {caption: "cos", value: "\\cos", meta: "cos", score: 40},
    {caption: "tg", value: "\\tg", meta: "tg", score: 40},
    {caption: "ctg", value: "\\ctg", meta: "ctg", score: 40},
    {caption: "log", value: "\\log", meta: "log", score: 40},
    {caption: "ln", value: "\\ln", meta: "log", score: 39},
    {caption: "arcsin", value: "\\arcsin", meta: "arcsin", score: 12},
    {caption: "arccos", value: "\\arccos", meta: "arccos", score: 12},
    {caption: "arctg", value: "\\arctg", meta: "arctg", score: 11},
    {caption: "arcctg", value: "\\arcctg", meta: "arcctg", score: 10},
    {caption: "text", value: "\\text", meta: "text", score: 20},
    {caption: "mathrm", value: "\\mathrm", meta: "mathrm", score: 10},
    {caption: "cup", value: "\\cup", meta: "∪", score: 40},
    {caption: "cap", value: "\\cap", meta: "∩", score: 40},
    {caption: "emptyset", value: "\\varnothing", meta: "∅", score: 50},
    {caption: "varnothing", value: "\\varnothing", meta: "∅", score: 30},
    {caption: "nothing", value: "\\varnothing", meta: "∅", score: 50},
    {caption: "mathbb", value: "\\mathbb", meta: "mathbb", score: 10},
    {caption: "int", value: "\\int\\limits", meta: "∫", score: 40},
    {caption: "lim", value: "\\lim\\limits", meta: "lim", score: 40},
    {caption: "alpha", value: "\\alpha", meta: "α", score: 15},
    {caption: 'varphi', valute: '\\varphi', meta: "φ", score: 39},
    {caption: 'phi', valute: '\\varphi', meta: "φ", score: 40},
    {caption: 'beta', valute: '\\beta', meta: "β", score: 40},
    {caption: 'Delta', valute: '\\Delta', meta: "Δ", score: 40},
    {caption: 'gamma', valute: '\\gamma', meta: "γ", score: 40},
    {caption: 'upsilon', valute: '\\upsilon', meta: "υ", score: 40},
    {caption: 'omega', valute: '\\omega', meta: "ω", score: 40},
    {caption: 'sigma', valute: '\\sigma', meta: "σ", score: 40},
];

const completer = {
  insertMatch: function (editor, cmd) {
    // Текущая позиция курсора
    const cursor = editor.selection.getCursor();
    // Вся строка, на которой находится курсор
    const line = editor.session.getLine(cursor.row);
    // Подстрока слева от курсора
    const lineBeforeCursor = line.slice(0, cursor.column);
    // Ищем последний участок, который соответствует шаблону
    // \? - опциональный слэш
    // [a-zA-Zа-яА-Я]+ - несколько букв (латиница/кириллица)
    // $ - конец строки (т.е. прямо у курсора)
    const match = lineBeforeCursor.match(/\\?[a-zA-Zа-яА-Я]+$/);
    if (match) {
      // Индекс начала совпадения
      const startIndex = match.index;
      // Индекс конца совпадения
      const endIndex = startIndex + match[0].length;
      // Создаём Range с координатами (row, colStart) -> (row, colEnd)
      const range = new Range(cursor.row, startIndex, cursor.row, endIndex);
      // Заменяем найденную подстроку на cmd.value
      editor.session.replace(range, cmd.value);
    } else {
      // Если ничего не подходит под регулярку,
      // просто вставляем как раньше
      editor.insert(cmd.value);
    }
  }
};

const customCompleter = {
    getCompletions: function (editor, session, pos, prefix, callback) {
        latexCommands.map(cmd => cmd.completer = completer);
        latexCommands.sort((a, b) => (b.score || 0) - (a.score || 0));
        callback(null, latexCommands);
    },
};
const customSnippetCompleter = {
  getCompletions(editor, session, pos, prefix, callback) {
    // Получаем сниппеты из snippetManager (или храните их статически в массиве)
    aceLatexSnippets.map(sn => {
      sn.meta = sn.meta || 'snippet';
      sn.score = sn.score || 1;
      sn.caption = sn.caption || sn.name;
      sn.snippet = sn.content;
      sn.value = sn.value || sn.content;
    });
    // Сортируем по score (DESC)
    aceLatexSnippets.sort((a, b) => (b.score || 0) - (a.score || 0));
    callback(null, aceLatexSnippets);
  },
  insertMatch(editor, data) {
    // Логика вставки (или используем стандартную insertSnippet)
    snippetManager.insertSnippet(editor, data.value);
  }
};

editor.completers.push(customCompleter);
editor.completers.splice(1, 1); // Удаляем local
editor.completers.splice(1, 1); // Удаляем "snippetCompleter"
console.warn(editor.completers);
editor.completers.unshift(customSnippetCompleter);

window.addEventListener('resize', function () {
    editor.resize();
});

const katexMacros = {
    '\\dv': '\\smash{\\mskip3mu\\vdots\\mskip3mu}',
    '\\le': '\\leqslant',
    '\\leq': '\\leqslant',
    '\\ge': '\\geqslant',
    '\\geq': '\\geqslant',
};

const katexConfig = {
    macros: katexMacros,
    strict: false,
    maxExpand: Infinity,
    output: 'html',
    throwOnError: false,
    errorColor: '#f00',
    delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '\\[', right: '\\]', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\(', right: '\\)', display: false}
    ],
};

const output = document.getElementById('output');


function getParm(parm) {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    return params.get(parm) || '';
}

const auth = getParm('auth');

const cache = new Map();


function toText(solObj) {
    if ('final_answer' in solObj) {
        const blocks = [];
        for (const [key, val] of Object.entries(solObj)) {
            if (key.startsWith('step')) {
                blocks.push(`
${key.slice(5)}
action: ${val.action}
solution: ${val.solution}
answer: ${val.answer}
`);
            }
        }
        blocks.push(`\nfinal_answer: ${solObj.final_answer}`);
        return blocks.join('\n');
    } else if ('answer' in solObj) {
        return solObj.answer;
    } else {
        return 'Ошибка алгорешателя: ' + (solObj.error || JSON.stringify(solObj));
    }
}


async function solveExpression(authKey, expression) {
    const url = '/solver';
    const response = await fetch(url, {
        method: 'POST', // Предположим, что метод POST, изменить если требуется
        headers: {
            'Authorization': authKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({expr: expression})
    });
    if (!response.ok) {
        throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    return await response.json();
}

async function solsProcessor(match) {
    let [both, cmd, parms] = match;
    cmd = cmd.trim().toLowerCase();
    parms = parms.trim()
    const joined = cmd + parms;
    let res = cache.get(joined);
    if (res !== undefined) {
        return res;
    }
    try {
        res = toText(await solveExpression(auth, both));
        if (res) {
            cache.set(joined, res);
        }
    } catch (e) {
        console.error(e);
        res = both;
    }
    return res;
}


function embedCalc(text) {
    let result = [];
    let inSingleDollar = false;
    let inDoubleDollar = false;
    let i = 0;

    while (i < text.length) {
        if (text.slice(i, i + 2) === '$$') {
            inDoubleDollar = !inDoubleDollar;
            result.push('$$');
            i += 2;
        } else if (text[i] === '$' && !inDoubleDollar) {
            inSingleDollar = !inSingleDollar;
            result.push('$');
            i += 1;
        } else if (text.slice(i, i + 7) === '<<calc ' && !inSingleDollar && !inDoubleDollar) {
            let j = i;
            while (j < text.length && text.slice(j, j + 2) !== '>>') {
                j += 1;
            }
            j += 2;  // To include the closing '>>'
            result.push('$');
            result.push(text.slice(i, j));
            result.push('$');
            i = j;
        } else {
            result.push(text[i]);
            i += 1;
        }
    }
    return result.join('');
}

const escLookup = {
    '&': "&amp;",
    '"': "&quot;",
    '\'': "&apos;",
    '<': "&lt;",
    '>': "&gt;"
};
function htmlEscape(s) {
    return s.replace( /[&"'<>]/g, c => escLookup[c] );
}

async function solsEmbedder(text) {
    const solverCallRe = /(?:<<|\[\[)\s*(\w+)\s*\|?\s*([\s\S]*?)\s*(?:>>|\]\])/g;
    let match;
    let resultText = '';
    let lastIndex = 0;
    text = text.split('\n').map(embedCalc).join('\n');
    const showTask = getParm('showtask');
    while ((match = solverCallRe.exec(text)) !== null) {
        resultText += text.slice(lastIndex, match.index); // Append text before the current match
        if (showTask && !match[0].includes('calc')) {
            console.log('task', match[0]);
            resultText += `\n\ntask:<<<<<${match[0]}>>>>>\n`;
        }
        resultText += await solsProcessor(match); // Process the current match and append the result
        lastIndex = solverCallRe.lastIndex; // Update the last index to the end of the current match
    }
    resultText += text.slice(lastIndex); // Append any remaining text after the last match

    const saveAllFinal = getParm('allfin');
    // Оставляем только последний final_answer, если не сказано иного
    if (!saveAllFinal) {
        const finalRe = /\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction)|(?:task:<<<))/g;
        const matches = [...resultText.matchAll(finalRe)];
        const numFinals = matches.length;

        if (numFinals > 1) {
            // Удаляем все совпадения, кроме последнего
            for (let i = 0; i < numFinals - 1; i++) {
                resultText = resultText.replace(matches[i][0], '');
            }
        }
    }
    return resultText;
}


function fixFormula(match, ldol, formula, rdol) {
    const leftBrRe = /(?<!\\left)(?<!\\left )(\(|\[|\\\{)/g;
    const rightBrRe = /(?<!\\right)(?<!\\right )(\)|\]|\\\})/g;
    const percentRe = /(?<!\\)%/g;
    const commaSepRe = /([^\d,]|^)(\d+),(\d+)(?=[^\d,]|$)/g;
    const killedSqrt = /sqrt\s*\\left\[([^\]]*?)\\right\]/g;
    if (ldol.length !== rdol.length) {
        ldol = '$$';
        rdol = '$$ (!!НЕПАРНЫЕ ДОЛЛАРЫ!!)';
    }
    formula = formula.replaceAll(leftBrRe, '\\left$1');
    formula = formula.replaceAll(rightBrRe, '\\right$1');
    formula = formula.replaceAll(killedSqrt, 'sqrt[$1]');
    const leftCnt = (formula.match(/\\left/g) || []).length;
    const rightCnt = (formula.match(/\\right/g) || []).length;
    if (leftCnt !== rightCnt) {
        formula = formula.replaceAll('\\left', '').replaceAll('\\right', '');
    }
    formula = formula.replaceAll(percentRe, '\\%');
    formula = formula.replaceAll(commaSepRe, '$1$2{,}$3');
    return `${ldol}${formula}${rdol}`;
}

function fixFormulas(text) {
    const fixFormulasRe = /(\${1,2})([^$\n]+?)(\${1,2})/g;
    return text.replace(fixFormulasRe, fixFormula);
}

function fixOddDollarLines(text) {
    const lines = text.split('\n');
    const fixedLines = lines.map(line => {
        const dollarCount = (line.match(/\$/g) || []).length;
        if (dollarCount % 2 !== 0) {
            return line + '$ (!!НЕ ХВАТАЕТ ＄!!)';
        }
        return line;
    });
    return fixedLines.join('\n');
}


function blockProcessor(match) {
    const [, task, num, act, sol, ans, fin, err] = match;
    const showTask = getParm('showtask');
    // Есть три случая: task, (num, act, sol, ans) и fin
    let resHtml = '';
    if (task !== undefined) {
        if (showTask) {
            resHtml += `<div class="rawTask"><code>${htmlEscape(task.slice(10, -7))}</code></div>`;
        }
    }
    if (act !== undefined) {
        blockNum += 1;
        resHtml += ``
            + `<div class="task">`
            + `<div class="num"> <span class="label">${blockNum}</span> </div>`
            + `<div class="step"> <span class="label">action:</span> ${act.trim()} </div>`
            + `<div class="step"> <span class="label">solution:</span> ${sol.trim()} </div>`
            + `<div class="step"> <span class="label">answer:</span> ${ans.trim()} </div>`
            + `</div>`
        ;
    }
    if (fin !== undefined) {
        blockNum = 0;
        resHtml += `<div class="final-answer"><span class="label">final_answer:</span> ${fin.trim()}</div>`;
    }
    if (err !== undefined) {
        resHtml += `<div class="error">${htmlEscape(err)}</div>`;
    }
    return resHtml;
}

async function schemeTextProcessing(text) {
    // const blockRe = /\s*"?(\d*)\s*[aA]ction:?\s+([\s\S]*?)\s*[sS]olution:?\s+([\s\S]*?)\s*[aA]nswer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|[fF]inal_answer)|\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction))/g;
    const blockRe = /\s*(task:<{3,}.*?>{3,}\s*)\s*|\s*"?(\d*)\s*[aA]ction:?\s+([\s\S]*?)\s*[sS]olution:?\s+([\s\S]*?)\s*[aA]nswer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|[fF]inal_answer)|\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction))|(Ошибка алгорешателя: .*)/g;
    // 0. Убираем слеши от процентов
    text = text.replaceAll('\\%', '%');
    // 1. Исправляем формулы.
    text = fixFormulas(text);
    text = fixOddDollarLines(text);
    // 1.5 Угловые скобки
    text = text.replaceAll(/\s*(?<!<)<(?!<)\s*/g, ' < ');
    text = text.replaceAll(/\s*(?<!>)>(?!>)\s*/g, ' > ');
    // 2. Вставляем решатели
    text = await solsEmbedder(text);
    console.log('==================================================');
    console.log(text.replaceAll(parConstT, '\n<br>\n'));
    console.log('==================================================');
    // 3. Процессим блоки
    let match;
    let resultText = '';
    let lastIndex = 0;

    while ((match = blockRe.exec(text)) !== null) {
        resultText += text.slice(lastIndex, match.index); // Append text before the current match
        resultText += blockProcessor(match); // Process the current match and append the result
        lastIndex = blockRe.lastIndex; // Update the last index to the end of the current match
    }
    resultText += text.slice(lastIndex); // Append any remaining text after the last match
    resultText = resultText.replaceAll(/\s*(?=<div class="final-answer">)/g, '');
    resultText = fixFormulas(resultText);
    return resultText;
}

const parConst = ' gZq8EbzRdl ';
const parConstT = parConst.trim();

function extMathParRemover(match) {
    return match.replaceAll(parConstT, ' ');
}

async function update() {
    blockNum = 0;
    try {
        const latexCode = editor.getValue();
        localStorage.setItem("raw", latexCode);
        let processedCode = await schemeTextProcessing(latexCode);
        processedCode = processedCode.replace(/(?:\r?\n[ \t]*){1,}/g, parConst);
        processedCode = processedCode.replaceAll(/\$\$(?:[^$]|\\\$)*\$\$/g, extMathParRemover);
        processedCode = processedCode.replaceAll(/\\\[[\s\S]*?\\\]/g, extMathParRemover);
        // Теперь нужно удалить parConst изнутри выделенных формул
        output.innerHTML = processedCode;
        renderMathInElement(output, katexConfig);
        let outputWithTex = output.innerHTML;
        outputWithTex = outputWithTex.replaceAll(parConstT, '\n<br>\n');
        output.innerHTML = outputWithTex;
        localStorage.setItem("rend", outputWithTex);
    } catch (err) {
        console.error(err);
    }
}

window.update = update;

const raw = localStorage.getItem("raw");
const rend = localStorage.getItem("rend");
if (raw && rend) {
    output.innerHTML = rend;
    editor.setValue(raw);
}
editor.session.on('change', update);
editor.on("paste", function (event) {
    let pastedText = event.text;
    // Check if the pasted text is surrounded by quotes
    if (pastedText.startsWith('"') && pastedText.endsWith('"')) {
        pastedText = pastedText.slice(1, -1);
    }
    pastedText = pastedText.replaceAll(/"\r?\n"/g, '');
    event.text = pastedText;
});
setTimeout(update, 100);


if (window.location.hostname === "127.0.0.1") {
    let ws;
    let retryInterval = 1000;

    function connectWebSocket() {
        ws = new WebSocket("ws://127.0.0.1:8179/ws/reload");

        ws.onmessage = function (event) {
            if (event.data === "reload") {
                cache.clear();
                setTimeout(update, 0);
            }
        };

        ws.onclose = function () {
            console.log("WebSocket закрыт. Переподключение...");
            setTimeout(connectWebSocket, retryInterval);
        };

        ws.onerror = function (error) {
            console.error("WebSocket ошибка:", error);
            ws.close();
        };

        ws.onopen = function () {
            console.log("Переподключились. Обновляем...");
            setTimeout(update, 0);
        }
    }

    connectWebSocket();
}
