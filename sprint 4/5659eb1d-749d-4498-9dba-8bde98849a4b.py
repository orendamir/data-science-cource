#!/usr/bin/env python
# coding: utf-8

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Привет! Спасибо, что сдал задание:) Ты проделал большую работу. Далее в файле мои комментарии ты сможешь найти в ячейках, аналогичных данной ( если рамки комментария зелёные - всё сделано правильно; жёлтые - есть замечания, но не критично; красные - нужно переделать). Не удаляй эти комментарии и постарайся учесть их в ходе выполнения проекта. 
# 
# </div>

# # Шаг 1. Откройте файл с данными и изучите общую информацию
# 

# <div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>
# 
# Надо обязательно прикреплять описание проекта, иначе не понятно в чём суть вообще твоей работы

# In[338]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats as st


# In[339]:


calls = pd.read_csv('/datasets/calls.csv')
internet = pd.read_csv('/datasets/internet.csv')
messages = pd.read_csv('/datasets/messages.csv')
tariffs = pd.read_csv('/datasets/tariffs.csv')
users = pd.read_csv('/datasets/users.csv')


# In[340]:


tariffs.info()


# - tariff_name — название тарифа
# - rub_monthly_fee — ежемесячная абонентская плата в рублях
# - minutes_included — количество минут разговора в месяц, включённых в абонентскую плату
# - messages_included — количество сообщений в месяц, включённых в абонентскую плату
# - mb_per_month_included — объём интернет-трафика, включённого в абонентскую плату (в мегабайтах)
# - rub_per_minute — стоимость минуты разговора сверх тарифного пакета (например, если в тарифе 100 минут разговора в месяц, то со 101 минуты будет взиматься плата)
# - rub_per_message — стоимость отправки сообщения сверх тарифного пакета
# - rub_per_gb — стоимость дополнительного гигабайта интернет-трафика сверх тарифного пакета (1 гигабайт = 1024 мегабайта)

# In[341]:



    #Сразу же переименуем колонку с названием тарифа, чтобы в дальнейшем у нас была возможность применить merge по ней.
    

tariffs = tariffs.rename(columns={'tariff_name': 'tariff'})


# In[342]:


tariffs


# In[343]:


users.info()


# 
# - user_id — уникальный идентификатор пользователя
# - first_name — имя пользователя
# - last_name — фамилия пользователя
# - age — возраст пользователя (годы)
# - reg_date — дата подключения тарифа (день, месяц, год)
# - churn_date — дата прекращения пользования тарифом (если значение пропущено, то тариф ещё действовал на момент выгрузки данных)
# - city — город проживания пользователя
# - tariff — название тарифного плана

# In[344]:


users


# In[345]:


calls.info()


# - id — уникальный номер звонка
# - call_date — дата звонка
# - duration — длительность звонка в минутах
# - user_id — идентификатор пользователя, сделавшего звонок

# In[346]:


calls


# In[347]:


messages.info()


# - id — уникальный номер сообщения
# - message_date — дата сообщения
# - user_id — идентификатор пользователя, отправившего сообщение

# In[348]:


messages


# In[349]:


internet.info()


# - id — уникальный номер сессии
# - mb_used — объём потраченного за сессию интернет-трафика (в мегабайтах)
# - session_date — дата интернет-сессии
# - user_id — идентификатор пользователя

# In[350]:


internet


# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Молодец, что провёл первичный анализ полученных данных, это всегда быстро помогает понять с чем предстоит работать, по выводам нареканий нет - всё верно и точно
# </div>

# # Шаг 2. Подготовьте данные
# 

# In[351]:


calls['duration'] = calls['duration'].apply(np.ceil)
NZ = calls['duration'] > 0
calls['duration'].where(NZ, 1, inplace=True)


#  - применил метод np.ceil для признака, тем самым получив верхнее значение в минутах;
#  - заменил нули на 1 – минимальное значение сессии звонка для оператора. (по хорошему нужно сходить к коллегам и уточнить что с выгрузкой)

# In[352]:


internet['mb_used'] = internet['mb_used'].apply(np.ceil)
NZI = internet['mb_used'] > 0
internet['mb_used'].where(NZI, 1, inplace=True)


# - применим метод np.ceil для признака, тем самым получив верхнее значение в минутах;
# - заменим нули на 1 – минимальное значение сессии.

# In[353]:


calls['call_date'] = pd.to_datetime(calls['call_date'], format='%Y-%m-%d')
users['reg_date'] = pd.to_datetime(users['reg_date'], format='%Y-%m-%d')
messages['message_date'] = pd.to_datetime(messages['message_date'], format='%Y-%m-%d')
internet['session_date'] = pd.to_datetime(internet['session_date'], format='%Y-%m-%d')


# Преобразуем тип данных даты, чтоб в последующем извлечь месяц из даты

# In[354]:


calls['duration'] = calls['duration'].astype('int64')
internet['mb_used'] = internet['mb_used'].astype('int64')


# In[355]:


total = pd.DataFrame()


# Создадим пустой ДатаФрейм

# In[356]:


calls['month'] = calls['call_date'].dt.month


# In[357]:


calls_by_month = calls.pivot_table(
    index=['month', 'user_id'],
    values='duration',
    aggfunc=['count', 'sum']
)


# In[358]:


calls_by_month


# In[359]:


tmp_df = pd.DataFrame(calls_by_month.to_records())


# In[360]:


total['user_id'] = tmp_df['user_id']
total['month']   = tmp_df['month']
total['calls']   = tmp_df.iloc[:, 2]
total['minutes'] = tmp_df.iloc[:, 3]


# In[361]:


total


# In[362]:


messages['month'] = messages['message_date'].dt.month


# In[363]:


messages_by_month = messages.pivot_table(
    index=['month', 'user_id'],
    values='id',
    aggfunc='count'
)


# In[364]:


messages_by_month


# In[365]:


tmp_df = pd.DataFrame(messages_by_month.to_records()).rename(columns={'id': 'messages'})


# In[366]:


tmp_df


# In[367]:


total = total.merge(tmp_df, on=['user_id', 'month'], how='outer')


# In[368]:


total


# In[369]:


internet['month'] = internet['session_date'].dt.month


# In[370]:


internet_by_month = internet.pivot_table(
    index=['month', 'user_id'],
    values='mb_used',
    aggfunc='sum'
)


# In[371]:


internet_by_month


# In[372]:


tmp_df = pd.DataFrame(internet_by_month.to_records())


# In[373]:


total = total.merge(tmp_df, on=['user_id', 'month'], how='outer')


# In[374]:


total.info()


# После формирования датафрейма по месяцам появились пропуски. Такое ощущение, что некоторые пользователи в некоторые месяцы пользовались не всеми услугами. Например, кто-то только мобильным интернетом. Заполним пропуски нулями и позже посмотрим на распределение.

# In[375]:


na = ['calls', 'minutes', 'messages']

for f in na:
    # При соединении датафреймов Pandas привел типы к float64 из-за пропусков,
    # поэтому явно приведем их к int64
    total[f] = total[f].fillna(0).astype('int64')


# In[376]:


total.info()


# In[377]:


total.head()


# In[378]:


total = total.merge(users, on='user_id', how='left').merge(tariffs, on='tariff', how='left')


# In[379]:


total['minutes_over']  = total['minutes'] - total['minutes_included']
total['messages_over'] = total['messages'] - total['messages_included']
total['mb_used_over']  = total['mb_used'] - total['mb_per_month_included']


# In[380]:


total.head()


# Положительные значения указывают на перерасход. Отрицательные на остаток в рамках тарифа.
# 
# 

# In[381]:


def calc_monthly_revenue(row):
    
    
    minutes_price = 0
    messages_price = 0
    mb_used_price = 0
    
    # стоимость дополнительных минут
    if row['minutes_over'] > 0:
        minutes_price = row['minutes_over'] * row['rub_per_minute']

    # стоимость дополнительных сообщений
    if row['messages_over'] > 0:
        messages_price = row['messages_over'] * row['rub_per_message']

    # стоимость дополнительного трафика
    if row['mb_used_over'] > 0:
        mb_used_price = (row['mb_used_over'] / 1024) * row['rub_per_gb']
    
    return minutes_price + messages_price + mb_used_price


# In[382]:


total['rub_monthly_fee_over'] = total.apply(calc_monthly_revenue, axis=1)
total['rub_monthly_fee_total'] = total['rub_monthly_fee'] + total['rub_monthly_fee_over']


# In[383]:


total = pd.DataFrame(
    total[['month', 'tariff', 'user_id', 'city',
           'calls', 'minutes', 'messages', 'mb_used',
           'minutes_over', 'messages_over', 'mb_used_over',
           'rub_monthly_fee_over', 'rub_monthly_fee_total']]
)


# Избавились от промежуточных расчетных колонок

# In[384]:


total.head()


# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Этап предобработки закончен, со всеми действиями и выводами согласен, замечательно. Так же порадовало что всё делишь на отдельные ячейки и пишешь выводы, можно приступать к основной части анализа</div>

# # Шаг 3. Проанализируйте данные

# In[391]:


values = ['minutes', 'messages', 'mb_used', 'rub_monthly_fee_over', 'rub_monthly_fee_total']


# In[ ]:





# In[395]:


tariff_monthly_costs = total.pivot_table(
    index=['tariff', 'month'],
    values=values
)


# In[396]:


tariff_monthly_costs


# In[397]:


smart_monthly_costs = tariff_monthly_costs.loc['smart']
smart_monthly_costs


# In[398]:


ultra_monthly_costs = tariff_monthly_costs.loc['ultra']
ultra_monthly_costs


# In[399]:


tariff_usage = tariff_monthly_costs.pivot_table(
    index='tariff',
    values=values
)
tariff_usage


# Минуты разговора, количество сообщений и объём интернет-трафика в среднем необходимые пользователям каждого тарифа в месяц
# 

# ### Вывод
# -  Пользователи тарифа Ультра более активны
# -  пользователи тарифа Смарт тратят в среднем в 6 раз больше на дополнительные пакеты услуг. 
# -  Оператору больше денег приносит тариф Ультра, даже с учетом того, что в среднем пользователи не выходят за границы тарифных лимитов, а пользователи тарифа Смарт не тратят столько денег, чтобы перегнать стоимость тарифа Ультра.
# - Таким образом, для пользователя выгоднее тариф Смарт

# In[400]:


moscow = total['city'] == 'Москва'
total['city'].where(moscow, 'Другой регион', inplace=True)

city_monthly_costs = total.pivot_table(
    index=['city', 'month'],
    values=values
)


# In[402]:


city_usage = city_monthly_costs.pivot_table(
    index='city',
    values=values
)
city_usage


# ### Вывод
# - По средним значениям выручки пользователей Москвы и регионов мы видим, что разница не весомая.
# - Кол-во использованных минут и смс не практически не отличается
# - В Москве чуть больше потребляют трафика – ожидаемо с учетом покрытия и скорости

# In[405]:


smart_costs = total.query("tariff == 'smart'")


# In[406]:


smart_costs['minutes'].describe()


# In[408]:


ultra_costs = total.query("tariff == 'ultra'")


# In[409]:


ultra_costs['minutes'].describe()


# In[414]:


plt.hist(smart_costs['minutes'], bins=50, label='smart')
plt.hist(ultra_costs['minutes'], bins=50, label='ultra', alpha=0.7)
plt.legend(loc='upper right')
plt.show()


# <div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>
# 
# не забывай подписывать оси на графиках и указывать название для графика

# In[1]:


<div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>

не забывай подписывать оси на графиках и указывать название для графикаsmv = np.var(smart_costs['minutes'], ddof=1)
umv = np.var(ultra_costs['minutes'], ddof=1)


# In[423]:


smv


# In[424]:


umv


# ### Звонки
# 
# - Смарт станд. отклонение 194.871174  дисперсия 37974.774627825
# - Ультра стандю отклонение 325.738740 дисперсия 106105.72682307787

# In[425]:


smart_costs['messages'].describe()


# In[426]:


ultra_costs['messages'].describe()


# In[427]:


plt.hist(smart_costs['messages'], bins=50, label='smart')
plt.hist(ultra_costs['messages'], bins=50, label='ultra', alpha=0.7)
plt.legend(loc='upper right')
plt.show()


# <div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>
# 
# Графики точно нужно строить детальнее, иначе так из графика не понятно, что изображено, если не залазить в код, а заказчики в будущем точно не будут копать в коде, чтобы понять, что перед ними изображено

# In[428]:


<div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>

Графики точно нужно строить детальнее, иначе так из графика не понятно, что изображено, если не залазить в код, а заказчики в будущем точно не будут копать в коде, чтобы понять, что перед ними изображеноssv = np.var(smart_costs['messages'], ddof=1)
usv = np.var(ultra_costs['messages'], ddof=1)


# In[429]:


ssv


# In[430]:


usv


# ### СМС
# 
# - Смарт станд. отклонение 28.227876  дисперсия 796.8129584480083
# - Ультра стандю отклонение 47.804457 дисперсия 2285.266142544674
# 

# In[431]:


smart_costs['mb_used'].describe()


# In[432]:


ultra_costs['mb_used'].describe()


# In[433]:


plt.hist(smart_costs['mb_used'], bins=50, label='smart')
plt.hist(ultra_costs['mb_used'], bins=50, label='ultra', alpha=0.7)
plt.legend(loc='upper right')
plt.show()


# In[434]:


siv = np.var(smart_costs['mb_used'], ddof=1)
uiv = np.var(ultra_costs['mb_used'], ddof=1)


# In[435]:


siv


# In[436]:


uiv


# ### Интернет
# - Смарт станд. отклонение (Мб) 5871.037024 дисперсия 34469075.73833619
# - Ультра стандю отклонение (Мб) 9952.830482 дисперсия 99058834.60600853

# <div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>
# 
# Тут всё абсолютно верно, верные выводы, но стоило бы строить больше разнообразных визуализаций, это будет очень важным навыком , который точно пригодится тебе в будущем, так как в любой аналитике графики являются наглядным подтверждением твоих выводов

# # Шаг 4. Проверьте гипотезы
# 

# Мы рассматриваем две генеральные сопокупности – пользователей разных тарифов мобильного оператора. Проверим две (двусторонние) гипотезы о равенстве среднего двух генеральных совокупностей по взятым из них выборкам. Чтобы понять, различается ли средняя выручка пользователей разных тарифов и населенных пунктов, значима ли разница между средними значениями, проведем статистические тесты.

# ### Cредняя выручка пользователей тарифов «Ультра» и «Смарт» различается

# - Средняя выручка пользователя тарифа "Смарт": 1145 руб
# - Средняя выручка пользователя тарифа "Ультра": 2038 руб

# Нулевая гипотеза - Средняя выручка пользователей тарифов "Ультра" и "Смарт" не различается
# 
# альтернативная гипотеза  - Средняя выручка пользователей тарифов "Ультра" и "Смарт" различается

# In[437]:


alpha = .01

results = st.ttest_ind(
    smart_costs['rub_monthly_fee_total'], 
    ultra_costs['rub_monthly_fee_total'])

print('p-значение:', results.pvalue)

if (results.pvalue < alpha):
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")


# Средняя выручка по тарифам не одинакова, и практически нулевая вероятность говорит о том, что случайно получить такое отличие в значениях практически не получится. Следовательно, средняя выручка пользователей тарифов "Ультра" и "Смарт" действительно различается и наша гипотеза подтвердилась

# ### Cредняя выручка пользователей из Москвы отличается от выручки пользователей из других регионов

# - Средняя выручка пользователей из Москвы: 1483 руб
# - Средняя выручка пользователей из других регионов: 1398 руб

# Нулевая гипотеза - Cредняя выручка пользователей из Москвы не отличается от выручки пользователей из других регионов
# альтернативная гипотеза  - Cредняя выручка пользователей из Москвы отличается от выручки пользователей из других регионов
# 

# In[442]:


alpha = .05

moscow = total.query("city == 'Москва'")['rub_monthly_fee_total']
other_cities = total.query("city == 'Другой регион'")['rub_monthly_fee_total']

results = st.ttest_ind(moscow, other_cities)

print('p-значение:', results.pvalue)

if (results.pvalue < alpha):
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")


# Полученное значение p-value говорит о том, что хотя средняя выручка пользователей из Москвы и регионов неодинакова, с вероятностью в почти 52% такое различие можно получить случайно. Как мы уже знаем, это слишком большая вероятность, чтобы делать вывод о значимом различии между средними выручками. Таким образом, средняя выручка пользователей из Москвы не отличается от выручки пользователей из других регионов, и наша гипотеза не подтвердилась.
# 
# 

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Гипотезы проверены, молодец!)

# # Шаг 5. Напишите общий вывод
# 

#  Потвердилась только первая гипотеза Средняя выручка пользователей тарифов "Ультра" и "Смарт" различается

# Более выгоднай тариф:
# - для оператора Ультра
# - для пользователя Смарт

# <div style="border:solid  orange  2px; padding: 20px"> <h1 style="color: orange ; margin-bottom:20px">Комментарий наставника</h1>
# 
# В выводах стоит отражать все полученные результаты и желательно так же приводить цифры, полученные в ходе выполнения проекта

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Работа принята!) Ты проделал отличную работу и я очень рад, что у тебя всё получается!) Надеюсь так будет и в будущем и ты останешься полностью доволен данным курсом!) Удачи тебе в следующих проектах)

# In[ ]:




