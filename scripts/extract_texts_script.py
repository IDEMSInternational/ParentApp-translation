import json
import os

path = os.getcwd().replace('\\', '//')
json_decode_template = json.load(
    open(path + "//inputs//input_template.json", encoding='utf-8'))
json_decode_global = json.load(
    open(path + "//inputs//input_global.json", encoding='utf-8'))

ignore = ('.json', '.png', '.svg', '.mp3', '.mp4')
result = []
excluded_types = ('nested_properties', 'template', 'image', 'audio', 'video', 'animated_section',
                  'display_group', 'lottie_animation')
end_variable_characters = (' ', ':', ';', ',', '!', '?', '@')


def process_rows(val, result, source_type):
    for item in val:
        if not 'exclude_from_translation' in item or not bool(item.get('exclude_from_translation')) == True:
            item_value = item.get('value')
            value_type = str(item.get('type'))
            if not value_type in excluded_types:
                if isinstance(item_value, str):
                    value_string = str(item_value).strip()
                    matched_expressions=[]
                    if source_type =='template':
                        if item.get('_dynamicFields')!=None and item.get('_dynamicFields').get('value') != None:
                            for matched_expression in item.get('_dynamicFields').get('value'):
                                if matched_expression.get('matchedExpression')!= None:
                                    matched_expressions.append(matched_expression.get('matchedExpression'))
                    elif source_type =='global':
                        if str(value_string).count('@') > 0:
                            begin_str= str(value_string).find('@')
                            end_str= end_str=min(str(value_string).find(' ', begin_str+1) | len(value_string), \
                                    str(value_string).find('!', begin_str+1) | len(value_string), \
                                    str(value_string).find('?', begin_str+1) | len(value_string), \
                                    str(value_string).find('@', begin_str+1) | len(value_string))
                            matched_expressions.append(str(value_string[begin_str:]).strip())
                    add_to_result(value_string, matched_expressions, result, source_type)
                if isinstance(item_value, list):
                    i=-1
                    matched_expressions=[]
                    if item.get('_dynamicFields')!=None:
                        i=0
                        matched_expression_list= item.get('_dynamicFields').get('value')
                    for list_item in item_value:
                        if 'text:' in str(list_item):
                            begin_str = str(list_item).find('text:')+5
                            end_str = str(list_item).find('|', begin_str)
                            if end_str > 0:
                                value_string=str(list_item[begin_str:end_str]).strip()
                                print(value_string, end_str)
                            else:
                                value_string=str(list_item[begin_str:]).strip()
                                #print(value_string)
                            if i>=0:
                                if matched_expression_list.get(i) != None:
                                    for matched_expression in matched_expression_list.get(i):
                                        if matched_expression.get('matchedExpression')!= None:
                                            matched_expressions.append(matched_expression.get('matchedExpression'))
                                i=i+1
                            add_to_result(value_string,matched_expressions, result, source_type)
                        if not 'text:' in str(list_item):
                            print("Unexpected list element" + str(list_item))
            if item.get('rows')!=None :
                process_rows(item.get('rows'), result, source_type)

def add_to_result(value_string, matched_expressions, result, source_type):
    if not value_string.endswith(ignore) and \
            not value_string.startswith('https') and not value_string.startswith('plh_') and \
            not value_string == 'true' and not value_string == 'false' and \
            value_string != 'None' and value_string!="" and \
            not value_string.isnumeric() and \
            not (value_string.startswith('@') and (" " not in value_string)):
        result_item = {}
        result_item['SourceText'] = value_string
        result_item['text'] = value_string
        result_item['type'] = source_type
        if len(matched_expressions) == 1:
            result_item['note'] = 'The string ' + \
               matched_expressions[0] \
                + ' should not be translated.'
        if len(matched_expressions) >1:
            note_text = 'The following strings should not be translated: '
            for matched_expression in matched_expressions:
                note_text = note_text+'\n     '+matched_expression

            result_item['note'] = note_text
        result.append(result_item)


def set_source_type(source_type, result):
    if source_type == 'template':
        for i in range(0, len(json_decode_template)):
            val = json_decode_template[i]['rows']
            source_type=source_type
            process_rows(val, result, source_type)
    elif source_type == 'global':
        for i in range(0, len(json_decode_global)):
            val = json_decode_global[i]['rows']
            source_type =source_type
            process_rows(val, result, source_type)
#---------------------------------------------------------------------------------------
template_src = 'template'
global_src = 'global'
#set_source_type(template_src, result)
set_source_type(global_src, result)
# --------------------------------------------------------------------------------------

print(len(result))
result = list(filter(({}).__ne__, result))
print(len(result))
result = [i for n, i in enumerate(result) if i not in result[n + 1:]]
print(len(result))

# ---------------------------------------------------------------------------------------

with open(path + '//Outputs//output_global.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False)

# ----------------------------
res = [d['text'] for d in result if 'text' in d]
print('Number of characters for translation in template.json: ', sum(len(str(i)) for i in res))
print('Number of words for translation in template.json: ', sum(len(str(i).split()) for i in res))
