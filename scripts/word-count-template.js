var fs = require('fs');
var path = require("path");
var input_path = path.join(__dirname, "../Outputs/output-template.json");
var json_string = fs.readFileSync(input_path).toString();
var sheet_obj = JSON.parse(json_string);

var word_count = 0;
console.log("The current word count is ",word_count);

sheet_obj.forEach(translation_obj=>{
   // console.log("The current text is ",translation_obj.text);
    word_count = word_count + WordCount(translation_obj.text.toString());
   // console.log("The current word count is ",word_count);
});

console.log("The total word count is ",word_count);


function WordCount(str) { 
    return str.split(" ").length;
  }