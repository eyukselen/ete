import xml.etree.ElementTree as ET

xml_file = 'langs.model.xml'

tree = ET.parse(xml_file)

root = tree.getroot()

print(root)
print(root.attrib)


def ppxml(root, level=0):
    for node in root:
        print(' ' * level + node.tag)
        print(' ' * level + str(node.attrib))
        print(' ' * level + str(len(list(node))))
        if len(list(root)) > 0:
            ppxml(node, level + 2)


ppxml(root)
