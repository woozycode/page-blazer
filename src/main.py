import os
import sys
import logging
import shutil
import pathlib
from textnode import TextNode, TextType
from markdown_blocks import markdown_to_html_node
from htmlnode import ParentNode

logger = logging.getLogger(__name__)

basepath = sys.argv[0]
if basepath is None:
    basepath = "/"

def static_to_public(source_dir:str, destination_dir:str) -> None:
    logger.info("Copying static files to docs...")

    if "static" not in source_dir:
        raise ValueError("Error: invalid source directory")
    if "docs" not in destination_dir:
        raise ValueError("Error: invalid destination directory")
    if not os.path.exists(source_dir):
        raise ValueError(f"Error: {source_dir} does not exist")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Delete contents of destination dir to ensure clean copy
    for filename in os.listdir(destination_dir):
        file_path = os.path.join(destination_dir, filename)
        try:
            if os.path.isfile(file_path):
                logger.info(f"Deleting file {file_path}")
                os.remove(file_path)
            elif os.path.isdir(file_path):
                logger.info(f"Deleting directory {file_path}")
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(msg=f"Error: failed to delete due to {e}")
            print(f"Error: failed to delete due to {e}")
            raise

    # Copy contents of source dir to destination dir
    for filename in os.listdir(source_dir):
        src_file_path = os.path.join(source_dir, filename)
        dest_file_path = os.path.join(destination_dir, filename)
        try:
            if os.path.isfile(src_file_path):
                logger.info(f"Copying file {src_file_path} to {dest_file_path}")
                shutil.copy(src=src_file_path, dst=dest_file_path)
            elif os.path.isdir(src_file_path):
                logger.info(f"Copying directory {src_file_path} to {dest_file_path}")
                os.mkdir(dest_file_path)
                logger.info("Gathering child elements from directory...")
                for child_file in os.listdir(src_file_path):
                    child_src_file_path = os.path.join(src_file_path, child_file)
                    child_dest_file_path = os.path.join(dest_file_path, child_file)
                    logger.info(f"Copying file {child_src_file_path} to {child_dest_file_path}")
                    shutil.copy(src=child_src_file_path, dst=child_dest_file_path)
        except Exception as e:
            logger.error(msg=f"Error: failed to copy due to {e}")
            print(f"Error: failed to copy due to {e}")
            raise


def extract_title(markdown:str) -> str:
    if not isinstance(markdown, str):
        with open(markdown, 'r') as f:
            md = f.read()
            if not md.startswith("#"):
                raise Exception("Error: no heading in markdown")
            parts = md.split("\n")
            h1_header = parts[0]
        return h1_header.split("#")[0].strip()
    if not markdown.startswith("#"):
        raise Exception("Error: no heading in markdown")
    return markdown.split("# ")[0].strip()


def generate_page(basepath:str, from_path:str, template_path:str, dest_path:str) -> None:
    logger.info(f"Generating page from {from_path} to {dest_path}...")
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    logger.info("Reading from markdown file...")
    with open(from_path, 'r') as markdown_file:
        markdown = markdown_file.read()

    logger.info("Reading from template file...")
    with open(template_path, 'r') as template_file:
        template = template_file.read()

    logger.info("Converting markdown to html node...")
    html_node = markdown_to_html_node(markdown)

    logger.info("Converting html node to html...")
    html_string = html_node.to_html()

    logger.info("Extracting page title...")
    page_title = extract_title(markdown)

    logger.info("Updating html template...")
    template = template.replace("{{ Title }}", page_title)
    template = template.replace("{{ Content }}", html_string)
    template = template.replace('href="/', f'href="{basepath}')
    template = template.replace('src="/', f'src="{basepath}')

    try:
        logger.info(f"Writing updated html page to {dest_path}")
        if not os.path.exists(dest_path):
            path_parts = os.path.split(dest_path)
            if not os.path.exists(path_parts[0]):
                os.makedirs(path_parts[0])

        with open(dest_path, "w") as f:
            f.write(template)
    except Exception as e:
        raise


def generate_pages_recursive(basepath:str, dir_path_content:str, template_path:str, dest_dir_path:str) -> None:
    directory_items = os.listdir(dir_path_content)
    logger.info(f"Gathering items from directory {dir_path_content}...")
    for item in directory_items:
        item_src_path = os.path.join(dir_path_content, item)
        logger.info(f"Examining item at path {item_src_path}")
        if os.path.isfile(item_src_path):
            item_dest_path = os.path.join(dest_dir_path, item)
            item_src_pure_path = pathlib.PurePath(item_src_path)
            item_parents = item_src_pure_path.parts
            logger.info(f"Item parents: {item_parents}")
            item_src_path_stem = "/".join(item_parents[1:])
            item_dest_path_stem = "/".join(item_parents[1:-1])
            logger.info(f"Item source path stem: {item_src_path_stem}")
            logger.info(f"Item dest path stem: {item_dest_path_stem}")
            item_dest_path = os.path.join(dest_dir_path, item_dest_path_stem, "index.html")
            logger.info(f"Item destination path: {item_dest_path}")
            generate_page(basepath=basepath, from_path=item_src_path, template_path=template_path, dest_path=item_dest_path)
        elif not os.path.isfile(item_src_path):
            logger.info(f"Item at path {item_src_path} is a directory")
            generate_pages_recursive(basepath=basepath, dir_path_content=item_src_path, template_path=template_path, dest_dir_path=dest_dir_path)


def main() -> None:
    logging.basicConfig(filename="page-blazer.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode="w")
    logger.info("Starting...")
    static_to_public(source_dir="static", destination_dir="docs")
    generate_pages_recursive(basepath=basepath, dir_path_content="content", template_path="template.html", dest_dir_path="docs")
    logger.info("Finished")


main()
