// Indent wrapped lines in order to keep them out of the line-numbering column.

// One of these methods should work for a given browser; though this means
// possibly running the hangingIndent routine 3 times, it also ensures we successfully
// wrap all code blocks, all the time, on all tested browsers.
document.addEventListener('DOMContentLoaded', hangingIndentAllCodeBlocks, false);
window.addEventListener('load', hangingIndentAllCodeBlocks, false);
hangingIndentAllCodeBlocks();

// Apply hanging indent CSS to wrapped lines in each div.highlight code block
function hangingIndentAllCodeBlocks() {
    var blocks = document.getElementsByClassName('highlight');
    for (var i = 0; i < blocks.length; i++) {
        hangingIndentCodeBlock(blocks[i]);
    }
}

// Apply hanging indent CSS to wrapped lines in given block
function hangingIndentCodeBlock(block) {
    var lineNums = block.querySelectorAll('.lineno');
    if (lineNums.length == 0) {
        return;
    }

    // Calculate actual width of a character in the line numbers column
    var first = lineNums[0];
    var text = first.innerText || first.textContent;
    var charWidth = first.offsetWidth / text.length;

    // Adjustment width is width of line number column plus 1 more character-width
    // for the trailing space that comes after the span.lineno element
    var adjustWidth = charWidth * (text.length + 1);

    // Indent the entire block by adjustWidth ...
    block.firstChild.style.marginLeft = adjustWidth + 'px';

    // ... and correspondingly de-indent just the starting line-number <span> of
    // each line-of-code, resulting in only wrapped lines of code being indented
    // past the column of line numbers
    for (var i = 0; i < lineNums.length; i++) {
        lineNums[i].style.marginLeft = -adjustWidth + 'px';
    }
}