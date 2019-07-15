.PHONY: clean

PokeIconEmerald.ttf: PokeIconEmerald.ttx
	ttx -f -o $@ $<

PokeIconEmerald.ttx: Roboto-Regular.ttx buildfont.py
	python buildfont.py $< $@

Roboto-Regular.ttx: Roboto-Regular.ttf
	ttx -f -o $@ $<

Roboto-Regular.ttf:
	wget -O $@ 'https://github.com/google/fonts/raw/master/apache/roboto/Roboto-Regular.ttf'

clean:
	rm *.ttx *.ttf
