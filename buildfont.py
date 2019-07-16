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

    return (lastglyphid + 1, newttglyph, newmtx)


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
        if pokemonnamechars[i] == '!':
            pokemonnamechars[i] = 'exclam'
        if pokemonnamechars[i] == '?':
            pokemonnamechars[i] = 'question'
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


def addpixelglyphs(root):
    for x in range(32):
        for y in range(32):
            glyphname = 'poke_pixel_{}_{}'.format(x, y)
            _, ttglyph, mtx = addglyph(root, glyphname)

            fontx = x * 64
            fonty = (31 - y) * 64

            mtx.attrib['lsb'] = str(fontx)

            contour = ET.SubElement(ttglyph, 'contour')

            pt = ET.SubElement(contour, 'pt')
            pt.attrib['on'] = '1'
            pt.attrib['x'] = str(fontx)
            pt.attrib['y'] = str(fonty)

            pt = ET.SubElement(contour, 'pt')
            pt.attrib['on'] = '1'
            pt.attrib['x'] = str(fontx)
            pt.attrib['y'] = str(fonty + 64)

            pt = ET.SubElement(contour, 'pt')
            pt.attrib['on'] = '1'
            pt.attrib['x'] = str(fontx + 64)
            pt.attrib['y'] = str(fonty + 64)

            pt = ET.SubElement(contour, 'pt')
            pt.attrib['on'] = '1'
            pt.attrib['x'] = str(fontx + 64)
            pt.attrib['y'] = str(fonty)

            instructions = ET.SubElement(ttglyph, 'instructions')


def pokeicontocolr(colrnode, glyphname, pokeicon, palettelist, palettemap):
    im = Image.open(pokeicon)
    # print(im)
    assert im.size == (32, 64)
    im = im.convert('RGBA')

    colorglyph = ET.SubElement(colrnode, 'ColorGlyph')
    colorglyph.attrib['name'] = glyphname

    for x in range(32):
        for y in range(32):
            r, g, b, a = im.getpixel((x, y))
            if a == 0:
                continue

            # XXX Not strictly necessary
            assert a == 255

            # print(r, g, b)
            if (r, g, b) in palettemap:
                paletteindex = palettemap[(r, g, b)]
            else:
                paletteindex = len(palettelist)
                palettelist.append((r, g, b))
                palettemap[(r, g, b)] = paletteindex

            pixglyph = 'poke_pixel_{}_{}'.format(x, y)
            layernode = ET.SubElement(colorglyph, 'layer')
            layernode.attrib['name'] = pixglyph
            layernode.attrib['colorID'] = str(paletteindex)


def build_pokemon_font(inttxfn, outttxfn):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(inttxfn)
    root = tree.getroot()
    # svgnode = ET.SubElement(root, 'SVG')
    colrnode = ET.SubElement(root, 'COLR')
    version = ET.SubElement(colrnode, 'version')
    version.attrib['value'] = "0"
    cpalnode = ET.SubElement(root, 'CPAL')
    version = ET.SubElement(cpalnode, 'version')
    version.attrib['value'] = "0"
    ligaturenode = root.find(
        "./GSUB/LookupList/Lookup[@index='4']/LigatureSubst")
    # print(ligaturenode)

    addpixelglyphs(root)

    palettelist = []
    palettemap = {}

    pokecount = 0
    pokemonlist = os.listdir('pokeemerald/graphics/pokemon')
    pokemonlist.sort()
    pokemonlist = pokemonlist[:50]
    # print(pokemonlist)
    # Need to invert order so that ligatures are generated in the right order
    # so that shared prefixes (e.g. mew/mewtwo or porygon/porygon2) work
    for pokemon in pokemonlist[::-1]:
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
        newid, _, _ = addglyph(root, newname)
        filename = 'pokeemerald/graphics/pokemon/{}/icon.png'.format(pokemon)
        svgdata = pokeicontosvg(filename)
        # print(newid)
        # addsvg(svgnode, newid, svgdata)
        pokeicontocolr(colrnode, newname, filename, palettelist, palettemap)
        addligature(ligaturenode, pokemon, newname)

        pokecount += 1

        # break

    for unown in "abcdefghijklmnopqrstuvwxyz!?":
        if unown == '!':
            unown_ = 'exclamation_mark'
        elif unown == '?':
            unown_ = 'question_mark'
        else:
            unown_ = unown
        newname = 'poke_unown_' + unown_
        print(newname)
        newid, _, _ = addglyph(root, newname)
        filename = \
            'pokeemerald/graphics/pokemon/unown/icon_{}.png'.format(unown_)
        svgdata = pokeicontosvg(filename)
        # print(newid)
        # addsvg(svgnode, newid, svgdata)
        pokeicontocolr(colrnode, newname, filename, palettelist, palettemap)
        addligature(ligaturenode, 'unown{}'.format(unown), newname)

        pokecount += 1

        # break
    print("Processed {} Pokemon".format(pokecount))

    # Add palette data
    numpal = ET.SubElement(cpalnode, 'numPaletteEntries')
    numpal.attrib['value'] = str(len(palettelist))
    palnode = ET.SubElement(cpalnode, 'palette')
    palnode.attrib['index'] = '0'
    for i in range(len(palettelist)):
        r, g, b = palettelist[i]
        colornode = ET.SubElement(palnode, 'color')
        colornode.attrib['index'] = str(i)
        colornode.attrib['value'] = '#{:02X}{:02X}{:02X}'.format(r, g, b)

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
