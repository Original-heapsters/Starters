from AuxClasses import getty


# Just log in, we will keep the session for you
s = getty.Session('','','', '')

s.search('Trendy topic here', items=10, from_item=1)
#s.buy(ID_to_buy, 1024 * 1024) # We get the download link here !