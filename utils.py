def equals_case_insensitive(string1, string2):
    s1 = string1.replace('\n', '').replace('\t', '').replace(' ', '')
    s2 = string2.replace('\n', '').replace('\t', '').replace(' ', '')
    return s1.lower() == s2.lower()


def unescape_html_entities(word):
    word = word.replace('&quot;', '\'').replace('&#039;', '\'')
    return word
