#!/usr/bin/env python
# coding: utf-8

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Привет! Очень рад, что ты уже почти закончил 1 этап Практикума!) Спасибо, что сдал задание:) Ты проделал большую работу. Далее в файле мои комментарии ты сможешь найти в ячейках, аналогичных данной ( если рамки комментария зелёные - всё сделано правильно; жёлтые - есть замечания, но не критично; красные - нужно переделать). Не удаляй эти комментарии и постарайся учесть их в ходе выпфолнения проекта. 
# 
# </div>

# # Сборный проект 1
# Вы работаете в интернет-магазине «Стримчик», который продаёт по всему миру компьютерные игры.
# 
# Из открытых источников доступны исторические данные о продажах игр, оценки пользователей и экспертов, жанры и платформы (например, Xbox или PlayStation).
# 
# 🎯 Вам нужно выявить определяющие успешность игры закономерности. Это позволит сделать ставку на потенциально популярный продукт и спланировать рекламные кампании. Перед вами данные до 2016 года.
# 
# Представим, что сейчас декабрь 2016 г., и вы планируете кампанию на 2017-й. Нужно отработать принцип работы с данными. Не важно, прогнозируете ли вы продажи на 2017 год по данным 2016-го или же 2027-й — по данным 2026 года.

# ## 1. Общая информация

# In[58]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats as st


# In[59]:


games = pd.read_csv('/datasets/games.csv')


# In[60]:


games.info()


# In[61]:


games.head()


# ### Описание данных
# - Name — название игры
# - Platform — платформа
# - Year_of_Release — год выпуска
# - Genre — жанр игры
# - NA_sales — продажи в Северной Америке (миллионы долларов)
# - EU_sales — продажи в Европе (миллионы долларов)
# - JP_sales — продажи в Японии (миллионы долларов)
# - Other_sales — продажи в других странах (миллионы долларов)
# - Critic_Score — оценка критиков (максимум 100)
# - User_Score — оценка пользователей (максимум 10)
# - Rating — рейтинг от организации ESRB (англ. Entertainment Software Rating Board). Эта ассоциация определяет рейтинг компьютерных игр и присваивает им подходящую возрастную категорию.

# In[62]:


# Количество игр в датасете
len(games['Name'].unique())


# In[63]:


# Представленные платформы 
games['Platform'].value_counts()


# In[64]:


# Жанры
games['Genre'].value_counts()


# In[65]:


# Рейтинг
games['Rating'].value_counts()


# In[66]:


# Кол-во полных дубликатов
games.duplicated().sum()


# In[67]:


# Кол-во пропусков
games.isna().sum()


# In[68]:


games.query("User_Score == 'tbd'")


# tbd - to be defined 
# Рейтинг пользователь содержит пропуски, а так же значени TBD (to be defined) (2424 записи) данные которые предпологалось заполнить позднее, и для них на момент выгрузки не нашлось значений  

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
#     
# Отличное начало, радует,что проводишь первичный анализ полученных данных и пишешь выводы

# ## 2. Подготовка данных

# In[69]:


games.columns = [a.lower() for a in list(games.columns)]


# In[70]:


games.info()


# Название столбцов привели к нижнему регистру

# In[71]:


def missing_data_in(col):
    
    # Возвращает Series с пропусками в указанной колонке
    
    return games[games[col].isnull()]


# In[72]:


missing_data_in('name')


# О этих двух играх ничего не известно, так что мы не сможем заменить данные. наиблее верным решением будет удалить эти сроки

# In[73]:


games.drop(missing_data_in('name').index , inplace=True)


# In[74]:


missing_data_in('year_of_release')


# In[75]:


games.query('name == "Madden NFL 2004" ')


# Обратим внимание что некоторые игры представлены на разных платформах, и в нашем частном случае год пропущен только на PS2 соответсвенно мы можем восстаноить эти данные 

# In[76]:


not_null_values = games[games['year_of_release'].notnull()]


# In[77]:


def fill_year_of_release(row, **kwargs):
    col = 'year_of_release'
    rows = not_null_values[not_null_values['name'] == row['name']]
   
    if len(rows) > 0:
        return rows.iloc[0][col]
    
    return row[col]


# In[78]:


games['year_of_release'] = games.apply(fill_year_of_release, axis=1).astype('Int64')


# In[79]:


len(missing_data_in('year_of_release'))


# Осталось 146 пропусков, для них ничего не нашлось, придётмя оставить как есть

# In[80]:


# Преобразуем пропуски `tbd` в NaN
tbd = games['user_score'] != 'tbd'
games['user_score'].where(tbd, np.nan, inplace=True)


# In[81]:


games.isnull().sum()


# К сожалению оставшиеся пропуски мы не сможем ничем заполнить (и еще их очень много), будем анализировать данные как есть

# In[82]:


games['year_of_release'] = games['year_of_release'].astype('Int64')
games['critic_score'] = games['critic_score'].astype('Int64')
games['user_score'] = games['user_score'].astype('float64')


# Преобразовали  типы данных

# In[83]:


games['total_sales'] = games['na_sales'] + games['eu_sales'] + games['eu_sales'] + games['jp_sales'] + games ['other_sales']


# In[84]:


games.head()


# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
#     
# Данные предобработали и разобрались с неточностями, отлично, можно приступать и к анализу

# ## 3. Исследовательский анализ данных
# 

# ### 1) Посмотрите, сколько игр выпускалось в разные годы. Важны ли данные за все периоды?
# 

# In[85]:


games_per_year = (
    games[['name', 'year_of_release']]
        .drop_duplicates()
        .pivot_table(index='year_of_release', values='name', aggfunc='count')
        .sort_values('year_of_release', ascending=False)
)


# In[86]:



plt

(
    games_per_year
        .plot(figsize=(6, 3), colormap='plasma', grid=True, legend=False, title='Количество игр по годам')
        .set(xlabel='Год релиза', ylabel='Кол-во')
)

plt.show()


# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
#     
# Наглядная визуализация получилась, здорово, что не забывавешь подписывать оси на графиках и сам график

# На мой взгляд данные за весь период нам будут не очень инетерсны, так как основной рост в кол-ве выпускаемых игр пришелся на время запуска Sony Playstation + когда компьютеры стали более популярны в частных целях и они стали более доступные в домашних условиях использования. Мне кажется можно ограничиться последним десятилетием 
# 

# ### 2) Посмотрите, как менялись продажи по платформам. Выберите платформы с наибольшими суммарными продажами и постройте распределение по годам. За какой характерный срок появляются новые и исчезают старые платформы?

# In[87]:


#  Функция глобальные продажи по платформам
def total_sales_per_platform_for(df):
    return (
        df
            .pivot_table(index='platform', values='total_sales', aggfunc='sum')
            .sort_values('total_sales', ascending=False)
    )


# In[88]:


# Столбчатая диаграмма глобальных продаж
def bar_plot(df):
    (
        df
            .plot(kind='bar', y='total_sales', figsize=(10, 5), grid=True, legend=False)
            .set(xlabel='Платформа', ylabel='Глобальные продажи')
    )
    plt.show()


# In[89]:


bar_plot(total_sales_per_platform_for(games))


# Выберем платформы с наибольшими глобальными продажами, например, первые 5 из списка выше и построим распределение по годам.
# 
# 

# In[90]:


top5 = total_sales_per_platform_for(games).head(5)


# In[91]:


top5


# In[92]:


def yearly_total_sales_by_platform(name, df):
    
    #Глобальные продажи по платформе по годам
    
    return (
        df
            .query("platform == @name")
            .pivot_table(index='year_of_release', values='total_sales', aggfunc='sum')
            .sort_values('year_of_release', ascending=False)
    )


# In[93]:


# Линейный график глобальных продаж по платформе по годам
for platform in list(top5.index):
    yearly_total_sales_by_platform(platform, games)['total_sales'].plot(figsize=(10, 5), grid=True, label=platform)
    plt.xlabel("Год релиза", labelpad=10)
    plt.ylabel("Глобальные продажи", labelpad=50)
    plt.legend()


# ~ 10 лет срок жизни платформы. Таким образом, мы еще раз убедились, что данные за все периоды нам не понадобятся – достаточно определить актуальный период в 10 лет и смотреть на игры на современных платформах.

# In[94]:



actual_years = (games['year_of_release'] > 2006) & (games['year_of_release'] <= 2016)
actual_games = games.loc[actual_years]


# In[95]:


actual_years


# ### 3) Какие платформы лидируют по продажам, растут или падают? Выберите несколько потенциально прибыльных платформ.

# In[96]:


total_sales = total_sales_per_platform_for(actual_games)


# In[97]:


bar_plot(total_sales)


# In[98]:


# список платформ за актуальный период
platforms = list(total_sales.index)

# график из 6 строк
rows = 6
cols = (len(platforms) // rows)
fig, ax = plt.subplots(rows, cols)

# построение графиков продаж по каждой платформе
num = 0
for row in range(rows):
    for col in range(cols):
        platform = platforms[num]
        (
            yearly_total_sales_by_platform(platform, actual_games)['total_sales']
                .plot(ax=ax[row, col], figsize=(20, 20), grid=True, title=platform)
                .set(xlabel='Год релиза', ylabel='Глобальные продажи')
        )
        num += 1

plt.tight_layout()
plt.show()


# 
# По графикам видим, что несмотря на лидирующие продажи за актуальный период, эра большинства платформ подходит к концу и продажи значительно падают. Из перспективных – консоли нового поколения:
# 
# - PS4: ~100 млн.
# - XOne: ~40 млн.
# Из портативных только 3DS от Nintendo пока еще держится в топе по продажам за 2016 год (около 20 млн).
# 
# Объем продаж компьютерных игр с каждым годом все меньше.

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
#     
# С выводами согласен

# ### 4) Постройте график «ящик с усами» по глобальным продажам каждой игры и разбивкой по платформам. Велика ли разница в продажах? А в средних продажах на разных платформах?

# In[99]:


promising_platforms = ['PS4', 'XOne']

fig, axs = plt.subplots(1, 2, sharey=True)

# построение графиков продаж по каждой платформе
for num, platform in enumerate(promising_platforms):
    df = yearly_total_sales_by_platform(platform, actual_games)
    print(f"Среднее значение глобальных продаж игр для {platform}: {df['total_sales'].mean()}")
    df.boxplot('total_sales', ax=axs[num])
    axs[num].set_title(platform)

#plt.tick_params(labelcolor='none', bottom='off')
plt.subplots_adjust(left=0.1)
plt.show()


# Сумма глобальных продаж игр для PS4 примерно в 2 раза больше чем у Xbox One

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
#     
# Тут тоже всё верно

# ### 5) Посмотрите, как влияют на продажи внутри одной популярной платформы отзывы пользователей и критиков.

# In[100]:


ps4 = actual_games.query("platform == 'PS4'")
xone = actual_games.query("platform == 'XOne'")


# In[101]:


features = ['user_score', 'critic_score', 'total_sales']
ps4[features].corr()


# In[102]:


xone[features].corr()


# In[103]:



ps4.plot(x='user_score', y='total_sales', kind='scatter', title='PS4')
xone.plot(x='user_score', y='total_sales', kind='scatter', title='Xbox One', color='green')
plt.show()


# In[104]:


ps4.plot(x='critic_score', y='total_sales', kind='scatter', title='PS4')
xone.plot(x='critic_score', y='total_sales', kind='scatter', title='Xbox One', color='green')
plt.show()


# Выводы:
# 
# - Взаимосвязи между отзывами пользователей и продажами нет;
# - Взаимосвязь между отзывами критиков и продажами существует, однако не слишком большая;
# - Взаимосязь между отзывами критиков и отзывами пользователей существует, чуть большая чем между отзывами критиков и продажами.
# - Корреляция не говорит о причинно-следственной связи. И хотя по диаграммам рассеяния видим, что чем выше оценки критиков, тем выше продажи игр на обоих платформах, мы не можем утверждать, что высокие оценки критиками приводят к высоким продажам игр, а при покупке игры пользователи больше доверяют критикам, а не заядлым игроманам

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# очень детально подходишь к работе, верные выводы, здорово!)

# ### 6) Посмотрите на общее распределение игр по жанрам.

# In[105]:


(actual_games
    .pivot_table(index='genre', values='total_sales')
    .sort_values('total_sales', ascending=False)
    .plot(kind='bar', y='total_sales', figsize=(10, 5), grid=True, legend=False)
    .set(xlabel='Жанр', ylabel='Глобальные продажи'))

plt.show()


#  Самыми популярными жанрами
#  являются шутеры, платформеры, а также спортивные игры. Хуже всего продаются стратегии и квесты.

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
#     
# Платформы проанализированны и всё выполнено правильно, радует, что пишешь выводы! теперь можно посмотреть и на портреты пользователей по регионам

# ## 4. Портрет пользователя каждого региона
# 
# 

# #### North America
# 
# 

# In[106]:


plt.style.use('seaborn')


# In[107]:


region = 'na_sales'


# In[108]:


def top5_in_region(column):
    return (
        actual_games
            .pivot_table(index=column, values=region, aggfunc='sum')
            .sort_values(region, ascending=False)
            .head(5)
    )


# In[109]:


def sales_pie_by_region(df):
    (
        df
            .plot(kind='pie', y=region, autopct='%1.0f%%', figsize=(10, 5), legend=False)
            .set(ylabel='Продажи')
    )
    plt.show()


# ##### Самые популярные платформы (топ-5)
# 

# In[110]:


sales_pie_by_region(top5_in_region('platform'))


# В Северной Америке Самая популярная платформа XBox, это объясняется тем что произвоит её Microsoft

# ##### Самые популярные жанры (топ-5)
# 

# In[117]:


sales_pie_by_region(top5_in_region('genre'))


#  Экшены и шутеры – самые популярные жанры.

# ##### Влияет ли рейтинг ESRB на продажи
# 
# 

# In[112]:


sales_pie_by_region(top5_in_region('rating'))


# Большая часть продаж приходится на игры для детей 6+ (E) и лишь 29% приходится на взрослую аудиторию (М)

# #### Europe

# In[113]:


region = 'eu_sales'


# ##### Самые популярные платформы (топ-5)
# 

# In[116]:


sales_pie_by_region(top5_in_region('platform'))


# Самая популярная платформа Playstation, Xbox на втором месте

# ##### Самые популярные жанры (топ-5)
# 

# In[118]:


sales_pie_by_region(top5_in_region('genre'))


#  Экшены и шутеры – самые популярные жанры.

# ##### Влияет ли рейтинг ESRB на продажи
# 

# In[119]:


sales_pie_by_region(top5_in_region('rating'))


# В целом картина очень похожа на Северную америку, только игры для взрослых блиде поднятунись в играм из категории 6+

# #### Japan

# In[120]:


region = 'jp_sales'


# ##### Самые популярные платформы (топ-5)
# 

# In[121]:


sales_pie_by_region(top5_in_region('platform'))


# В Японии картина продаж кардинально меняется. Японцы много играют на портативных консолях типа Nintento (3)DS, PSP и пр. Здесь мы практически не видим присутствия Xbox в пятерке лидеров.
# 
# 

# ##### Самые популярные жанры (топ-5)
# 

# In[122]:


sales_pie_by_region(top5_in_region('genre'))


# Ролевые игры  – самые популярные. К слову, экшены отстают по продажам примерно в полтора раза.
# 
# 

# #### Влияет ли рейтинг ESRB на продажи
# 

# In[123]:


sales_pie_by_region(top5_in_region('rating'))


# В Японии хуже всего продаются игры для взрослой аудитории – всего 17% продаж.

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Портреты пользователей построены, все выводы правильные, продолжай в том же духе!

# ## 5. Проверка гипотез
# 

# Для каждой из приведенных ниже гипотез проверим две (двусторонние) гипотезы о равенстве среднего двух генеральных совокупностей по взятым из них выборкам. Чтобы понять, различаются ли пользовательские рейтинги и значима ли разница между средними значениями, проведем статистические тесты.

# #### Cредние пользовательские рейтинги платформ Xbox One и PC одинаковые
# Мы рассматриваем две генеральные сопокупности – игры на разных платформах.
# 
# - Нулевая гипотеза H₀:
# 
# Средние пользовательские рейтинги платформ Xbox One и PC одинаковые.
# 
# - Исходя из H₀ формулируем альтернативную гипотезу H₁:
# 
# Средние пользовательские рейтинги платформ Xbox One и PC различаются.
# 
# Пороговое значение alpha (критический уровень статистической значимости) зададим равным 3%. 

# In[124]:


alpha = .03


# In[129]:


pc = actual_games.query("platform == 'PC'")

results = st.ttest_ind(
    xone['user_score'],
    pc['user_score'],
    equal_var=False,  # Welch’s t-test, который не предполагает равенство дисперсий
    nan_policy='omit' # игнорируем пропуски
)

print('p-значение:', results.pvalue)

if (results.pvalue < alpha):
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")


# In[130]:


pc['user_score'].mean()


# In[131]:


xone['user_score'].mean()


# p-value получили равным ~3%. Если бы рейтинги пользователей НЕ отличались (наша нулевая гипотеза), то те различия, что мы фактически видим, могли бы получиться случайно лишь в 3% случаев. Это весьма маленькая вероятность. Таким образом, различия довольно высокие для предположения равенства рейтингов. Но так как мы задали жесткий уровень значимости (0.025), то говорим, что тем не менее не будем отклонять гипотезу, но со стандартным уровнем в 0.05 мы бы ее уже отвергли.
# 
# Гипотеза Средние пользовательские рейтинги платформ Xbox One и PC одинаковые подтвердилась.

# #### Средние пользовательские рейтинги жанров Action и Sports разные
# Мы рассматриваем две генеральные сопокупности – игры разных жанров.
# 
# - Нулевая гипотеза H₀:
# 
# Средние пользовательские рейтинги жанров Action и Sports одинаковые.
# 
# - Исходя из H₀ формулируем альтернативную гипотезу H₁:
# 
# Средние пользовательские рейтинги жанров Action и Sports различаются.
# 
# Пороговое значение alpha (критический уровень статистической значимости) зададим равным 5%.

# In[132]:


alpha = .05


# In[133]:


action = actual_games.query("genre == 'Action'")
sports = actual_games.query("genre == 'Sports'")

results = st.ttest_ind(
    action['user_score'],
    sports['user_score'],
    nan_policy='omit' # игнорируем пропуски
)

print('p-значение:', results.pvalue)

if (results.pvalue < alpha):
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")


# Средние пользовательские рейтинги различаются, и практически нулевая вероятность говорит о том, что случайно получить такое отличие в значениях практически не получится.
# 
# Гипотеза Средние пользовательские рейтинги жанров Action и Sports разные подтвердилась.

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Радует, что для проверки гипотез используешь правильные методы, выводы по результатам проверки тоже правильные, молодец

# ## 6. Общий вывод
# 

# 
# Тезисы:
# 
# - Платформы появляются и умирают в течение 10 лет.
# - Наиболее популярные на данный момент платформы – это Sony PlayStation 4 и Xbox One. Они появились пару лет назад и имеют потенциал роста.
# - В США и Европе лучше всего продаются шутеры и экшены.
# - Япония – отдельный рынок с уклоном в портативные консоли и ролевые игры.
# - Больше всего продаж приходятся на игры, разрешенные для детей.
# 
# Обе сформулированные гипотезы подтвердились:
# 
# - Средние пользовательские рейтинги платформ Xbox One и PC одинаковые.
# - Средние пользовательские рейтинги жанров Action и Sports разные.

# <div style="border:solid orange 2px; padding: 20px"> <h1 style="color:orange; margin-bottom:20px">Комментарий наставника</h1>
# 
# Вывод можно было бы написать и подробнее можно, а так же можно давать советы по использованию данного анализа в будущем

# <div style="border:solid green 2px; padding: 20px"> <h1 style="color:green; margin-bottom:20px">Комментарий наставника</h1>
# 
# Ты проделал колоссальную работу и я очень рад за тебя! Удачи на следующем этапе!

# In[ ]:





# In[ ]:




