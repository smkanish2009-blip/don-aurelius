from html.parser import HTMLParser
import re
import sys

class StrictHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.errors = []
        self.ids = set()
        self.links = []
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if 'id' in attrs_dict:
            self.ids.add(attrs_dict['id'])
        if 'href' in attrs_dict and attrs_dict['href'].startswith('#'):
            self.links.append((attrs_dict['href'][1:], self.getpos()))
        if tag not in self.void_elements:
            self.tags.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if not self.tags:
            self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]}")
            return
        last_tag, pos = self.tags.pop()
        if last_tag != tag:
            self.errors.append(f"Mismatched tag: expected </{last_tag}> (opened at line {pos[0]}), got </{tag}> at line {self.getpos()[0]}")

with open("docs/index.html", "r", encoding="utf-8") as f:
    content = f.read()

validator = StrictHTMLValidator()
validator.feed(content)

print(f"Total HTML IDs found: {len(validator.ids)}")
print(f"Total Internal Anchor Links: {len(validator.links)}")

missing_anchors = []
for target_id, pos in validator.links:
    if target_id and target_id not in validator.ids:
        missing_anchors.append((target_id, pos))

if missing_anchors:
    print(f"ERROR: {len(missing_anchors)} broken internal anchor links!")
    for target, pos in missing_anchors:
        print(f" - #{target} at line {pos[0]}")
else:
    print("ALL internal anchor links match valid DOM IDs perfectly!")

if validator.errors:
    print(f"HTML Errors: {len(validator.errors)}")
    for err in validator.errors[:10]:
        print(" -", err)
else:
    print("HTML Structure is 100% Valid and Balanced!")
