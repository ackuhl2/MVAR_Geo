import gmpy2

entrada_indice = int(input('Entre com o índice:'))
entrada_expoente = int(input('Entre com o expoente:'))
indice = gmpy2.mpz(entrada_indice)
expoente = gmpy2.mpz(entrada_expoente)

restos = []
for i in range(indice+1):
    dividend = pow(gmpy2.mpz(i+1), expoente)
    remainder = gmpy2.f_mod(dividend, indice)
    if remainder not in restos:
        restos.append(int(remainder))

print('Para o índice',indice,'e o expoente',expoente, ', são', len(restos),'restos diferentes:', sorted(restos))



