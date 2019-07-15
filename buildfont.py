import sys
import xml.etree.ElementTree as ET
from PIL import Image


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

    svgdata = pokeicontosvg('pokeemerald/graphics/pokemon/eevee/icon.png')

    svgnode = ET.SubElement(root, 'SVG')
    addsvg(svgnode, newid, svgdata)

    tree.write(outttxfn, encoding='utf-8', xml_declaration=True)


def pokeicontosvg(pokeicon):
    im = Image.open(pokeicon)
    print(im)
    assert im.size == (32, 64)
    im = im.convert('RGBA')

    svgroot = ET.Element('svg')
    svgroot.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
    svgroot.attrib['version'] = '1.1'
    # # DEBUG
    # svgroot.attrib['width'] = '2048'
    # svgroot.attrib['height'] = '2048'

    for x in range(32):
        for y in range(32):
            r, g, b, a = im.getpixel((x, y))
            if a == 0:
                continue

            # XXX Not strictly necessary
            assert a == 255

            print(r, g, b)

            rect = ET.SubElement(svgroot, 'rect')
            rect.attrib['width'] = '64'
            rect.attrib['height'] = '64'
            rect.attrib['x'] = str(x * 64)
            rect.attrib['y'] = str(-(32 - y) * 64)
            rect.attrib['fill'] = 'rgb({},{},{})'.format(r, g, b)

    svgdata = ET.tostring(svgroot).decode()
    print(svgdata)
    with open('test.svg', 'w') as f:
        f.write(svgdata)
    return svgdata


def main():
    if len(sys.argv) < 3:
        print("Usage: {} infile outfile".format(sys.argv[0]))
        sys.exit(1)

    infn = sys.argv[1]
    outfn = sys.argv[2]
    build_pokemon_font(infn, outfn)


if __name__ == '__main__':
    main()
