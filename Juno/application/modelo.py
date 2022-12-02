import matplotlib.pyplot as plt
def prever(ano_final, username):
    ano_inicial = 2023
    r = 0.007
    p0 = 214000000
    dt = 1

    # m = 0.03666667

    p = [p0]
    t = []
    for i in range(ano_final - ano_inicial):
        t.append(i)
        next = p[i]*(1 + r)*dt
        p.append(round(next))
        # r -= m
    t.append(t[-1] + 1)

    plt.figure(figsize=(10, 4))
    plt.plot(t, p)
    #plt.xlabel("Tempo Decorrido")
    #plt.ylabel("Populacao")
    plt.axis('off')
    plt.savefig(f'application/static/imgs/{username}{ano_final}.png', transparent=True)
    return p[-1], f'{username}{ano_final}.png'