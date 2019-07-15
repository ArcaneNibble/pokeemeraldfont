import sys
import xml.etree.ElementTree as ET


def addglyph(root, name):
    # Add to GlyphOrder
    glyphorder = root.find('GlyphOrder')
    lastglyph = glyphorder[-1]
    lastglyphid = int(lastglyph.attrib['id'])
    # print(glyphorder)
    # print(lastglyph.attrib['id'])

    newglyphorder = ET.SubElement(glyphorder, 'GlyphID')
    newglyphorder.attrib['id'] = str(lastglyphid + 1)
    newglyphorder.attrib['name'] = name

    # Add dummy TTGlyph
    glyf = root.find('glyf')
    newttglyph = ET.SubElement(glyf, 'TTGlyph')
    newttglyph.attrib['name'] = name
    newttglyph.attrib['xMin'] = '0'
    newttglyph.attrib['yMin'] = '0'
    newttglyph.attrib['xMax'] = '0'
    newttglyph.attrib['yMax'] = '0'

    # Add to hmtx (always 1 full em)
    hmtx = root.find('hmtx')
    newmtx = ET.SubElement(hmtx, 'mtx')
    newmtx.attrib['name'] = name
    newmtx.attrib['width'] = '2048'
    newmtx.attrib['lsb'] = '0'

    # Add to hdmxData
    hdmxData = root.find('hdmx').find('hdmxData')
    hdmxData.text += "{}: 9;\n".format(name)

    return lastglyphid + 1


TEST = '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
    <circle cx="1024" cy="-1024" r="1024" stroke="black" stroke-width="3" fill="red"/>
</svg>'''


def addcmap(root, codepoint, name):
    cmap = root.find('cmap')
    for cmaptable in cmap:
        if cmaptable.tag == 'tableVersion':
            continue

        print(cmaptable)
        mapentry = ET.SubElement(cmaptable, 'map')
        mapentry.attrib['code'] = "0x{:x}".format(codepoint)
        mapentry.attrib['name'] = name


def addsvg(svgnode, glyphid, svgdata):
    svgroot = ET.fromstring(svgdata)
    svgroot.attrib['id'] = "glyph{}".format(glyphid)
    svgdata = ET.tostring(svgroot).decode()
    print(svgdata)

    svgdoc = ET.SubElement(svgnode, 'svgDoc')
    svgdoc.attrib['startGlyphID'] = str(glyphid)
    svgdoc.attrib['endGlyphID'] = str(glyphid)
    svgdoc.text = svgdata


def build_pokemon_font(inttxfn, outttxfn):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(inttxfn)
    root = tree.getroot()

    newid = addglyph(root, 'poketest')
    print(newid)
    addcmap(root, 0xe000, 'poketest')

    svgnode = ET.SubElement(root, 'SVG')
    addsvg(svgnode, newid, TEST)

    tree.write(outttxfn, encoding='utf-8', xml_declaration=True)


def main():
    if len(sys.argv) < 3:
        print("Usage: {} infile outfile".format(sys.argv[0]))
        sys.exit(1)

    infn = sys.argv[1]
    outfn = sys.argv[2]
    build_pokemon_font(infn, outfn)


if __name__ == '__main__':
    main()
