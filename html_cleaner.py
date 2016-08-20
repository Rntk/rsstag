from html.parser import HTMLParser

class HTMLCleaner(HTMLParser):
    strings = []

    def handle_data(self, data):
        self.strings.append(data)

    def purge(self):
        self.strings = []

    def get_content(self):
        return self.strings;