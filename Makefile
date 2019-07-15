PokeIconEmerald.ttf: PokeIconEmerald.ttx
	ttx -f -o $@ $<

PokeIconEmerald.ttx: Roboto-Regular.ttx
	cp $< $@

Roboto-Regular.ttx: Roboto-Regular.ttf
	ttx -f -o $@ $<

Roboto-Regular.ttf:
	wget -O $@ 'https://github.com/google/fonts/raw/master/apache/roboto/Roboto-Regular.ttf'
