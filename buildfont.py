import os
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

        # print(cmaptable)
        mapentry = ET.SubElement(cmaptable, 'map')
        mapentry.attrib['code'] = "0x{:x}".format(codepoint)
        mapentry.attrib['name'] = name


def addsvg(svgnode, glyphid, svgdata):
    svgroot = ET.fromstring(svgdata)
    svgroot.attrib['id'] = "glyph{}".format(glyphid)
    svgdata = ET.tostring(svgroot).decode()
    # print(svgdata)

    svgdoc = ET.SubElement(svgnode, 'svgDoc')
    svgdoc.attrib['startGlyphID'] = str(glyphid)
    svgdoc.attrib['endGlyphID'] = str(glyphid)
    svgdoc.text = svgdata


def pokeicontosvg(pokeicon):
    im = Image.open(pokeicon)
    # print(im)
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

            # print(r, g, b)

            rect = ET.SubElement(svgroot, 'rect')
            rect.attrib['width'] = '64'
            rect.attrib['height'] = '64'
            rect.attrib['x'] = str(x * 64)
            rect.attrib['y'] = str(-(32 - y) * 64)
            rect.attrib['fill'] = 'rgb({},{},{})'.format(r, g, b)

    svgdata = ET.tostring(svgroot).decode()
    # print(svgdata)
    # with open('test.svg', 'w') as f:
    #     f.write(svgdata)
    return svgdata


def addligature(ligaturenode, pokemonname, glyphname):
    if pokemonname == "farfetch_d":
        pokemonname = "farfetch'd"
    if pokemonname == "ho_oh":
        pokemonname = "ho-oh"
    if pokemonname == "mr_mime":
        pokemonname = "mr mime"
    # if pokemonname == "nidoran_f":
    #     pokemonname = "nidoranf"
    # if pokemonname == "nidoran_m":
    #     pokemonname = "nidoranm"

    pokemonnamechars = list(pokemonname)
    for i in range(len(pokemonnamechars)):
        if pokemonnamechars[i] == '_':
            pokemonnamechars[i] = 'underscore'
            # assert False
        if pokemonnamechars[i] == "'":
            pokemonnamechars[i] = 'quotesingle'
        if pokemonnamechars[i] == '-':
            pokemonnamechars[i] = 'hyphen'
        if pokemonnamechars[i] == ' ':
            pokemonnamechars[i] = 'space'
        if pokemonnamechars[i] == '0':
            pokemonnamechars[i] = 'zero'
        if pokemonnamechars[i] == '1':
            pokemonnamechars[i] = 'one'
        if pokemonnamechars[i] == '2':
            pokemonnamechars[i] = 'two'
        if pokemonnamechars[i] == '3':
            pokemonnamechars[i] = 'three'
        if pokemonnamechars[i] == '4':
            pokemonnamechars[i] = 'four'
        if pokemonnamechars[i] == '5':
            pokemonnamechars[i] = 'five'
        if pokemonnamechars[i] == '6':
            pokemonnamechars[i] = 'six'
        if pokemonnamechars[i] == '7':
            pokemonnamechars[i] = 'seven'
        if pokemonnamechars[i] == '8':
            pokemonnamechars[i] = 'eight'
        if pokemonnamechars[i] == '9':
            pokemonnamechars[i] = 'nine'
    # print(pokemonnamechars)

    ligaset = ligaturenode.find(
        "./LigatureSet[@glyph='{}']".format(pokemonnamechars[0]))
    # print(ligaset)
    if ligaset is None:
        ligaset = ET.SubElement(ligaturenode, 'LigatureSet')
        ligaset.attrib['glyph'] = pokemonnamechars[0]

    ligaturenode = ET.SubElement(ligaset, 'Ligature')
    ligaturenode.attrib['components'] = ','.join(pokemonnamechars[1:])
    ligaturenode.attrib['glyph'] = glyphname


def build_pokemon_font(inttxfn, outttxfn):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(inttxfn)
    root = tree.getroot()
    svgnode = ET.SubElement(root, 'SVG')
    ligaturenode = root.find(
        "./GSUB/LookupList/Lookup[@index='4']/LigatureSubst")
    print(ligaturenode)

    pokecount = 0
    for pokemon in os.listdir('pokeemerald/graphics/pokemon'):
        if pokemon == 'circled_question_mark':
            continue
        if pokemon == 'double_question_mark':
            continue
        if pokemon == 'icon_palettes':
            continue
        if pokemon == 'question_mark':
            continue

        if pokemon == 'unown':
            # Needs special handling
            continue

        print(pokemon)

        newname = 'poke_' + pokemon
        newid = addglyph(root, newname)
        svgdata = pokeicontosvg(
            'pokeemerald/graphics/pokemon/{}/icon.png'.format(pokemon))
        # print(newid)
        addcmap(root, 0xe000 + pokecount, newname)
        addsvg(svgnode, newid, svgdata)
        addligature(ligaturenode, pokemon, newname)

        pokecount += 1

        # break
    print("Processed {} Pokemon".format(pokecount))

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
