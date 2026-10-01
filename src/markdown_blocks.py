from enum import Enum
from htmlnode import HTMLNode, ParentNode
from inline_markdown import text_to_textnodes
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    OLIST = "ordered_list"
    ULIST = "unordered_list"


def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown: str) -> ParentNode:
    markdown_blocks = markdown_to_blocks(markdown)
    children = []
    for block in markdown_blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode(tag="div", children=children, props=None)


def block_to_html_node(block: str) -> ParentNode:
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.OLIST:
        return olist_to_html_node(block)
    if block_type == BlockType.ULIST:
        return ulist_to_html_node(block)
    raise ValueError("Error: invalid block type")


def text_to_children(text: str) -> list[HTMLNode]:
    text_nodes = text_to_textnodes(text=text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node=text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block: str) -> ParentNode:
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(text=paragraph)
    return ParentNode(tag="p", children=children, props=None)


def heading_to_html_node(block: str) -> ParentNode:
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"Error: invalid heading level {level}")
    text = block[level + 1 :]
    children = text_to_children(text=text)
    return ParentNode(tag=f"h{level}", children=children, props=None)


def code_to_html_node(block: str) -> ParentNode:
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Error: invalid code block")
    text = block[4:-3]
    raw_text_node = TextNode(text=text, text_type=TextType.TEXT)
    child = text_node_to_html_node(text_node=raw_text_node)
    code = ParentNode(tag="code", children=[child])
    return ParentNode(tag="pre", children=[code], props=None)


def quote_to_html_node(block: str) -> ParentNode:
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Error: invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(text=content)
    return ParentNode(tag="blockquote", children=children, props=None)


def olist_to_html_node(block: str) -> ParentNode:
    items = block.split("\n")
    html_items = []
    for item in items:
        parts = item.split(". ", 1)
        text = parts[1]
        children = text_to_children(text=text)
        html_items.append(ParentNode(tag="li", children=children, props=None))
    return ParentNode(tag="ol", children=html_items, props=None)


def ulist_to_html_node(block: str) -> ParentNode:
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text=text)
        html_items.append(ParentNode(tag="li", children=children, props=None))
    return ParentNode(tag="ul", children=html_items, props=None)
