import io
from lxml import etree


xml_file = """
<section
 xmlns="http://www.mydomain.com/events"
 xmlns:bk="urn:loc.gov:books"
 xmlns:pi="urn:personalInformation"
 xmlns:isbn='urn:ISBN:0-111-2222-3'>
  <title>Book-Signing Event</title>
  <signing>
    <bk:author pi:title="Mr" pi:name="brook bookman"/>
    <book bk:title="Writing for Fun and Profit" isbn:number="123456789"/>
    <comment xmlns=''>What a great issue!</comment>
  </signing>
</section>"""


tree = etree.parse(io.StringIO(xml_file))
xmlns = tree.xpath('namespace-uri(.)')
node = tree.getroot()

print(node.tag)
print(node.nsmap)


for child in node.getchildren():
    print('== Start ==')
    print(etree.QName(child).localname)  # tag name wihtout namespace
    print(child.attrib.items())
    print('== End ==')

exit()


