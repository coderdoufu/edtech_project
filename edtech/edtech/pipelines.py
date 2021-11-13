# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from scrapy.exporters import JsonItemExporter
import re
import hanlp

def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

#检验是否全是中文字符
def is_all_chinese(strs):
    return not bool(re.search('[a-z]', strs))

class EdtechPipeline:
    def open_spider(self,spider):
        print('Start saving file')
        self.f = open('edtech/edtech/data/cn_sentences.json', 'wb')
        self.exporter = JsonItemExporter(
                self.f,
                ensure_ascii=False, 
                encoding='utf-8'
        )
        self.exporter.start_exporting()
        self.hanlp = hanlp.load('edtech/hanlpweight')
    def close_spider(self, spider):
        print('Done saving file')
        self.exporter.finish_exporting()
        self.f.close()
    def process_item(self, item, spider):
        clean_sentence = self.post_process_sentence(item['sentence'])
        if clean_sentence:
            item['sentence'] = clean_sentence
            self.exporter.export_item(item)
        return item
    def post_process_sentence(self,sentence:str):
        clean_sentence = remove_html_tags(sentence)
        clean_sentence = clean_sentence.strip()
        clean_sentence = clean_sentence.replace(" ", "")
        match_index = re.search('[._,，:\)]',clean_sentence)
        if match_index:
            number_sep_index,_ = match_index.span()
        else:
            number_sep_index = 1000
        if number_sep_index < 3:
            clean_sentence = clean_sentence[number_sep_index+1:]

        # remove quotes
        doc = self.hanlp(clean_sentence)
        ents = [e[0] for e in doc['ner/pku'] if e[1]=="nr"]
        has_person_name = len(ents) > 0

        criteria = is_all_chinese(clean_sentence) and not has_person_name

        if criteria:
            return clean_sentence
        else:
            return ''
