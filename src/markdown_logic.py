import re

from enum import Enum
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, ParentNode, LeafNode

class BlockType(Enum):
    PARAGRAPH = "p"
    HEADING = "h"
    CODE = "code"
    QUOTE = "blockquote"
    UNORDERED_LIST = "ul"
    ORDERED_LIST = "ol"

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
        else:
            splitted = old_node.text.split(delimiter)
            if len(splitted) == 1:
                new_nodes.append(old_node)
                continue
            if len(splitted) % 2 == 0:
                raise Exception(f"Delimiter: {delimiter} was not closed")
            for i in range(0, len(splitted), 2):
                if splitted[i] != "":
                    new_nodes.append(TextNode(splitted[i], TextType.TEXT))
                if i < len(splitted) - 1:
                    new_nodes.append(TextNode(splitted[i+1], text_type))
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        matches = extract_markdown_images(old_node.text)
        current_text = old_node.text
        for match in matches:
            alt = match[0]
            link = match[1]
            sections = current_text.split(f"![{alt}]({link})", 1)
            if len(sections[0]) > 0:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, link))
            current_text = sections[1]
        if len(current_text) > 0:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        matches = extract_markdown_links(old_node.text)
        current_text = old_node.text
        for match in matches:
            alt = match[0]
            link = match[1]
            sections = current_text.split(f"[{alt}]({link})", 1)
            if len(sections[0]) > 0:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.LINK, link))
            current_text = sections[1]
        if len(current_text) > 0:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    return [block.strip() for block in markdown.split("\n\n") if block.strip()]

def block_to_block_type(block):

    def validate_numbered_lines(block):
        lines = block.splitlines()
        for i in range(1, len(lines) + 1):
            if lines[i-1].startswith(f"{i}. ") == False:
                return False
        return True
    
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING
    if re.match(r"```(?:\n)(.*?)```", block, flags=re.DOTALL):
        return BlockType.CODE
    if re.match(r"^(> ?.*\n?)+$", block):
        return BlockType.QUOTE
    if re.match(r"^(- .*\n?)+$", block):
        return BlockType.UNORDERED_LIST
    if validate_numbered_lines(block):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent_block = ParentNode("div", [])

    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            parent_block.children.append(block_to_paragraph_nodes(block))
        elif block_type == BlockType.CODE:
            parent_block.children.append(block_to_code_node(block))
        elif block_type == BlockType.QUOTE:
            parent_block.children.append(block_to_quote_node(block.replace(">\n", "")))
        elif block_type == BlockType.UNORDERED_LIST:
            parent_block.children.append(block_to_unordered_list(block))
        elif block_type == BlockType.ORDERED_LIST:
            parent_block.children.append(block_to_ordered_list(block))
        elif block_type == BlockType.HEADING:
            parent_block.children.append(block_to_heading_node(block))
        else:
            raise ValueError("invalid block type")

    return parent_block

def text_to_children(text):
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]

def block_to_paragraph_nodes(block):
    return ParentNode("p", text_to_children(block.replace("\n", " ")))

def block_to_quote_node(block):
    return ParentNode("blockquote", text_to_children(block.replace("> ", "").replace("\n", " ")))

def block_to_unordered_list(block):
    return ParentNode("ul", [ParentNode("li", text_to_children(li[2:])) for li in block.split("\n")])

# to cover the amount upredictability of list item in ordered list 
# for example: "100. ", "1001. " and so on, 
# each line is splitted by " " with maximum split amount of 1
# and second part of split logic is chosen to filter out the list syntax
def block_to_ordered_list(block):
    return ParentNode("ol", [ParentNode("li", text_to_children(li.split(" ", 1)[1])) for li in block.split("\n")])

def block_to_heading_node(block):
    size = 0
    for char in block:
        if char == '#':
            size += 1
        else:
            break
    if size > 6:
        raise ValueError(f"heading size: {size} can't be more than 6")
    return ParentNode(f"h{size}", text_to_children(block.replace(f"{"#" * size} ", "")))

def block_to_code_node(block):
    return ParentNode("pre", [text_node_to_html_node(TextNode(block.replace("```", "").lstrip(), TextType.CODE))])

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if re.match(r"^# ", block):
            return block[2:].strip()
    raise Exception("no title has been found")
    