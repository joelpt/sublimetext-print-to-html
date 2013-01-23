// Indent wrapped lines in order to keep them out of the line-numbering column.

var rewrapped = false;  // Set to true after we wrap to prevent running the routine twice

// One of these methods should work for a given browser
document.addEventListener('DOMContentLoaded', rewrapAllCodeBlocks, false);
window.addEventListener('load', rewrapAllCodeBlocks, false);
rewrapAllCodeBlocks();

// Apply css to word-wrap and indent all the lines of code in each div.highlight code block
function rewrapAllCodeBlocks(force) {
    if (rewrapped && !force) {
        // Only rewrap one time unless force=true
        return;
    }
    var blocks = document.getElementsByClassName('highlight');
    for (var i = 0; i < blocks.length; i++) {
        rewrapCodeBlock(blocks[i]);
    }
    rewrapped = true;
}

// Apply css to indent wrapped lines
function rewrapCodeBlock(block) {
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