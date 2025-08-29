from datetime import date

price_before = None
i = 1
j = 0
while price_before == None:
    ago = 7
    ago += ( (-1)**j ) * (i)
    if ago == 0: price_before == 0
    else: 
        j += 1
        if j % 2 == 0: i += 1
        print(ago)
                        
# if price_before == 0: ppc = '?' # figure this out later
# else: ppc = ( (price_today - price_before) / price_before ) * 100