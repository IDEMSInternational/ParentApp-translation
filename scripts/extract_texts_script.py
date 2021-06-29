import json
import os

path = os.getcwd().replace('\\', '//')
json_decode_template = json.load(
    open(path + "//Inputs//input_template.json", encoding='utf-8'))
json_decode_global = json.load(
    open(path + "//inputs//input_global.json", encoding='utf-8'))
json_decode_tour = json.load(
    open(path + "//Inputs//input_tour.json", encoding='utf-8'))

json_decode_data_list = json.load(
    open(path + "//Inputs//input_data_list.json", encoding='utf-8'))

ignore_end = ('.json', '.png', '.svg', '.mp3', '.mp4')
ignore_start = ('https', '@', 'plh_', '!@', '+@', '!!@')
result = []
excluded_types = ('nested_properties', 'template', 'image', 'audio', 'video', 'animated_section',
                  'display_group', 'lottie_animation')
contain_key = ('title', 'text', 'in_text_title', 'short_title', 'tools')
end_variable_characters = (' ', ':', ';', ',', '!', '?', '@')


def process_rows(val, result, filename):
    for item in val:
        if filename == 'template' or filename == 'global':                
            if not 'exclude_from_translation' in item or not bool(item.get('exclude_from_translation')) == True:
                item_value = item.get('value')
                value_type = str(item.get('type'))
                if not value_type in excluded_types:
                    if isinstance(item_value, str):
                        value_string = str(item_value).strip()
                        matched_expressions=[]
                        if filename =='template':
                            if item.get('_dynamicFields')!=None and item.get('_dynamicFields').get('value') != None:
                                for matched_expression in item.get('_dynamicFields').get('value'):
                                    if matched_expression.get('matchedExpression')!= None:
                                        matched_expressions.append(matched_expression.get('matchedExpression'))
                        elif filename =='global':
                            get_matched_text(value_string, matched_expressions)
                        add_to_result(value_string, matched_expressions, result, filename)
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
                                    #print(value_string)
                                else:
                                    value_string=str(list_item[begin_str:]).strip()
                                    #print(value_string)
                                if i>=0:
                                    if matched_expression_list.get(i) != None:
                                        for matched_expression in matched_expression_list.get(i):
                                            if matched_expression.get('matchedExpression')!= None:
                                                matched_expressions.append(matched_expression.get('matchedExpression'))
                                    i=i+1
                                add_to_result(value_string,matched_expressions, result, filename)
                            if not 'text:' in str(list_item):
                                print("Unexpected list element" + str(list_item))
                if item.get('rows')!=None :
                    process_rows(item.get('rows'), result, filename)
        elif filename == 'data_list':
            if not 'exclude_from_translation' in item or not bool(item.get('exclude_from_translation')) == True:
                if item.get('_translatedFields') != None:
                    for elt in contain_key:
                        if str(elt) in item.get('_translatedFields'):
                            value_string = str(item.get('_translatedFields').get(str(elt)).get('eng')).strip()
                            #print(value_string, 'Ok', elt)
                            matched_expressions = []
                            get_matched_text(value_string, matched_expressions)
                            result.append(add_to_result(value_string, matched_expressions, result, filename))
        else:
            if not 'exclude_from_translation' in item or not bool(item.get('exclude_from_translation')) == True:
                value_type = str(item.get('type'))
                if 'title' in item and not value_type in excluded_types:
                    item_value_title = item.get('title')
                    value_title_string = str(item_value_title).strip()
                    matched_expressions=[]
                    get_matched_text(value_title_string, matched_expressions)
                    result.append(add_to_result(value_title_string, matched_expressions, result, filename))
                if 'message_text' in item and not value_type in excluded_types:
                    item_value_message = item.get('message_text')
                    value_message_string = str(item_value_message).strip()
                    matched_expressions=[]
                    get_matched_text(value_message_string, matched_expressions)
                    result.append(add_to_result(value_message_string, matched_expressions, result, filename))                            

def add_to_result(value_string, matched_expressions, result, filename):
    if not value_string.endswith(ignore_end) and \
            not value_string == 'true' and not value_string == 'false' and \
            value_string != 'None' and value_string!="" and \
            not value_string.isnumeric() and \
            not (value_string.startswith(ignore_start) and (" " not in value_string)):
        result_item = {}
        result_item['SourceText'] = value_string
        result_item['text'] = value_string
        result_item['type'] = filename
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

def get_matched_text(value_string, matched_expressions):
    if str(value_string).count('@') > 0:
        for txt in value_string.split():
            if '@' in txt:
                matched_expressions.append(txt)

result_glob = []
result_temp = []
result_tour = []
result_data_list = []
def set_filename(filename, result):
    if filename == 'template':
        for i in range(0, len(json_decode_template)):
            val = json_decode_template[i]['rows']
            filename = filename
            process_rows(val, result, filename)
    elif filename == 'global':
        for i in range(0, len(json_decode_global)):
            val = json_decode_global[i]['rows']
            filename = filename
            process_rows(val, result, filename)
    elif filename == 'tour':
        for i in range(0, len(json_decode_tour)):
            val = json_decode_tour[i]['rows']
            filename = filename
            process_rows(val, result, filename)
    elif filename == 'data_list':
        for i in range(0, len(json_decode_data_list)):
            val = json_decode_data_list[i]['rows']
            filename = filename
            process_rows(val, result, filename)
#---------------------------------------------------------------------------------------
template_src = 'template'
global_src = 'global'
tour_src = 'tour'
data_list_src = 'data_list'
set_filename(template_src, result_temp)
set_filename(global_src, result_glob)
set_filename(tour_src, result_tour)
set_filename(data_list_src, result_data_list)
# --------------------------------------------------------------------------------------
# Result from Template file
print(len(result_temp))
result_temp = list(filter(({}).__ne__, result_temp))
print(len(result_temp))
result_temp = [i for n, i in enumerate(result_temp) if i not in result_temp[n + 1:]]
print(len(result_temp))

# Result from Global file
print(len(result_glob))
result_glob = list(filter(({}).__ne__, result_glob))
print(len(result_glob))
result_glob = [i for n, i in enumerate(result_glob) if i not in result_glob[n + 1:]]
print(len(result_glob))
# ---------------------------------------------------------------------------------------

# Result from Tour file
# print(len(result_tour))
# result_tour = list(filter(({}).__ne__, result_tour))
# print(len(result_tour))
result_tour = [i for i in result_tour if i]
result_tour = [i for n, i in enumerate(result_tour) if i not in result_tour[n + 1:]]
print(len(result_tour))
# ---------------------------------------------------------------------------------------

# Result from Data list file
#print(len(result_data_list))
result_data_list = [i for i in result_data_list if i]
result_data_list = [i for n, i in enumerate(result_data_list) if i not in result_data_list[n + 1:]]
print(len(result_data_list))
# ---------------------------------------------------------------------------------------

with open(path + '//Outputs//output_template.json', 'w', encoding='utf-8') as json_file:
    json.dump(result_temp, json_file, ensure_ascii=False)

with open(path + '//Outputs//output_global.json', 'w', encoding='utf-8') as json_file:
    json.dump(result_glob, json_file, ensure_ascii=False)

with open(path + '//Outputs//output_tour.json', 'w', encoding='utf-8') as json_file:
    json.dump(result_tour, json_file, ensure_ascii=False)

with open(path + '//Outputs//output_data_list.json', 'w', encoding='utf-8') as json_file:
    json.dump(result_data_list, json_file, ensure_ascii=False)
# ----------------------------------------------------------------------------------------
reslt_temp = [d['text'] for d in result_temp if 'text' in d]
print('Number of characters for translation in template.json: ', sum(len(str(i)) for i in reslt_temp))
print('Number of words for translation in template.json: ', sum(len(str(i).split()) for i in reslt_temp))
print('----------------------------------------------------------')
reslt_glob = [d['text'] for d in result_glob if 'text' in d]
print('Number of characters for translation in global.json: ', sum(len(str(i)) for i in reslt_glob))
print('Number of words for translation in global.json: ', sum(len(str(i).split()) for i in reslt_glob))
print('----------------------------------------------------------')
reslt_tour = [d['text'] for d in result_tour if 'text' in d]
print('Number of characters for translation in tour.json: ', sum(len(str(i)) for i in reslt_tour))
print('Number of words for translation in tour.json: ', sum(len(str(i).split()) for i in reslt_tour))
print('----------------------------------------------------------')
reslt_data = [d['text'] for d in result_data_list if 'text' in d]
print('Number of characters for translation in data_list.json: ', sum(len(str(i)) for i in reslt_data))
print('Number of words for translation in data_list.json: ', sum(len(str(i).split()) for i in reslt_data))
print('----------------------------------------------------------')
# Result from all files
result_all = result_temp + result_glob + result_tour + result_data_list
print(len(result_all))
print('---------------------------------------')
result_all = [i for n, i in enumerate(result_all) if i not in result_all[n + 1:]]
#print(len(result_all))

with open(path + '//Outputs//output.json', 'w', encoding='utf-8') as json_file:
    json.dump(result_all, json_file, ensure_ascii=False)

reslt_all = [d['text'] for d in result_all if 'text' in d]
print('Number of characters for translation in outputs.json: ', sum(len(str(i)) for i in reslt_all))
print('Number of words for translation in outputs.json: ', sum(len(str(i).split()) for i in reslt_all))
