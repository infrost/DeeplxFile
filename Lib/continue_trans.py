
translated_path = './out/translated_result.txt'
text_extracted_path = './tmp/text_extracted.txt'
continue_path = './tmp/continue.txt'

def move_lines():


    # Read lines from translated_result.txt
    with open(translated_path, 'r', encoding='utf-8') as file:
        translated_lines = file.readlines()
    a = len(translated_lines)

    # Write the translated lines to continue.txt
    with open(continue_path, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

    # Read lines from text_extracted.txt
    with open(text_extracted_path, 'r', encoding='utf-8') as file:
        text_extracted_lines = file.readlines()

    remaining_text_extracted_lines = text_extracted_lines[a:]

    # Write the remaining lines back to text_extracted.txt
    with open(text_extracted_path, 'w', encoding='utf-8') as file:
        file.writelines(remaining_text_extracted_lines)


def prepend_to_translated_result():

    # Read lines from continue.txt
    with open(continue_path, 'r', encoding='utf-8') as file:
        continue_lines = file.readlines()

    # Read original lines from translated_result.txt
    with open(translated_path, 'r', encoding='utf-8') as file:
        translated_lines = file.readlines()

    # Prepend continue.txt content to translated_result.txt
    with open(translated_path, 'w', encoding='utf-8') as file:
        file.writelines(continue_lines + translated_lines)
