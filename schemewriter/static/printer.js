'use strict';
let blockNum = 0;

const macros = {
    '\\dv': '\\smash{\\mskip3mu\\vdots\\mskip3mu}',
    '\\le': '\\leqslant',
    '\\leq': '\\leqslant',
    '\\ge': '\\geqslant',
    '\\geq': '\\geqslant',
};

const katexConfig = {
    macros,
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


function fixFormula(match, ldol, formula, rdol) {
    const leftBrRe = /(?<!\\left)(\(|\[|\\\{)/g;
    const rightBrRe = /(?<!\\right)(\)|\]|\\\})/g;
    const percentRe = /(?<!\\)%/g;
    const commaSepRe = /([^\d,]|^)(\d+),(\d+)(?=[^\d,]|$)/g;
    if (ldol.length !== rdol.length) {
        ldol = '$$';
        rdol = '$$ (!!НЕПАРНЫЕ ＄!!)';
    }
    formula = formula.replaceAll(leftBrRe, '\\left$1');
    formula = formula.replaceAll(rightBrRe, '\\right$1');
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
    const [, num, act, sol, ans, fin] = match;
    if (fin === undefined) {
        blockNum += 1;
        return `<div class="task">`
            + `<div class="num"> <span class="label">${blockNum}</span> </div>`
            + `<div class="step"> <span class="label">action:</span> ${act.trim()} </div>`
            + `<div class="step"> <span class="label">solution:</span> ${sol.trim()} </div>`
            + `<div class="step"> <span class="label">answer:</span> ${ans.trim()} </div>`
            + `</div>`;
    } else {
        blockNum = 0;
        return `<div class="final-answer"><span class="label">final_answer:</span> ${fin.trim()}</div>`;
    }
}

function schemeTextProcessing(text) {
    const blockRe = /\s*"?(\d*)\s*[aA]ction:?\s+([\s\S]*?)\s*[sS]olution:?\s+([\s\S]*?)\s*[aA]nswer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|[fF]inal_answer)|\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction))/g;
    // 0. Убираем слеши от процентов
    text = text.replaceAll('\\%', '%');
    // 1. Исправляем формулы.
    text = fixFormulas(text);
    text = fixOddDollarLines(text);
    // 2. Процессим блоки
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

    return resultText;

}


function update(latexCode) {
    const parConst = ' gZq8EbzRdl ';
    blockNum = 0;
    try {
        let processedCode = schemeTextProcessing(latexCode);
        processedCode = processedCode.replace(/(?:\r?\n[ \t]*){1,}/g, parConst);
        output.innerHTML = processedCode;
        renderMathInElement(output, katexConfig);
        let outputWithTex = output.innerHTML;
        outputWithTex = outputWithTex.replaceAll(parConst.trim(), '\n<br>\n');
        output.innerHTML = outputWithTex;
    } catch (err) {
        output.innerHTML = err;
    }
}


window.update = update;
