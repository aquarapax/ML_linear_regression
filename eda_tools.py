import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

'''
Набор функций для EDA-анализа
'''
# def return_eda(df):
#     # Создание списка для хранения статистики
#     numeric_summary = []

#     # Вычисление статистики для каждого столбца
#     for column in df.columns:
#         if column == 'id':
#             continue
#         stats = {
#             'Параметр': column,
#             'Пропуски (%)': df[column].isnull().mean(),
#             'Max': df[column].max(),
#             'Min': df[column].min(),
#             'AVG': df[column].mean(),
#             'Медиана': df[column].median(),
#             'Дисперсия': df[column].var(),
#             'q0.1': df[column].quantile(0.1),
#             'q0.9': df[column].quantile(0.9),
#             'Q1': df[column].quantile(0.25),
#             'Q3': df[column].quantile(0.75),
#             'Дробные': (df[column] % 1 > 0).sum(),
#             'Var_type_df': df[column].dtype,
#             'nunique': df[column].nunique(), 
#             'count_0': (df[column] == 0).sum(),
#         }
#         numeric_summary.append(stats)

#     # Преобразование списка в DataFrame
#     eda_df = pd.DataFrame(numeric_summary)

#     # Установка 'Параметр' в качестве индекса
#     eda_df.set_index('Параметр', inplace=True)
#     return(eda_df)
import pandas as pd

def return_eda(df):
    # Создание списка для хранения статистики
    numeric_summary = []

    # Вычисление статистики для каждого столбца
    for column in df.columns:
        if column == 'id':
            continue
        stats = {
            'Параметр': column,
            'nan' : df[column].isna().sum(),
            'Пропуски (%)': df[column].isnull().mean(),
            'Max': df[column].max(),
            'Min': df[column].min(),
            'AVG': df[column].mean(),
            'Медиана': df[column].median(),
            'Дисперсия': df[column].var(),
            'q0.1': df[column].quantile(0.1),
            'q0.9': df[column].quantile(0.9),
            'Q1': df[column].quantile(0.25),
            'Q3': df[column].quantile(0.75),
            'Дробные': (df[column] % 1 > 0).sum(),
            'Var_type_df': df[column].dtype,
            'nunique': df[column].nunique(), 
            'count_0': (df[column] == 0).sum(),
        }

        # Вычисление IQR
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        # Определение границ для выбросов
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Подсчет выбросов
        outliers_left = (df[column] < lower_bound).sum()
        outliers_right = (df[column] > upper_bound).sum()

        # Добавление количества выбросов в статистику
        stats['Выбросы слева'] = outliers_left
        stats['Выбросы справа'] = outliers_right

        numeric_summary.append(stats)

    # Преобразование списка в DataFrame
    eda_df = pd.DataFrame(numeric_summary)

    # Установка 'Параметр' в качестве индекса
    eda_df.set_index('Параметр', inplace=True)
    return eda_df


def return_outliers(df, column_name):
    # Рассчитываем квартили и IQR
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1

    # Определяем границы для выбросов
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Находим выбросы (все строки, где sales_unit выходит за границы)
    outliers_df = df[(df[column_name] < lower_bound) | (df[column_name] > upper_bound)]
    outliers_df = outliers_df.sort_values(by=column_name, ascending=True)
    # Выводим результат
    return(outliers_df)

def return_boxplot(df, title_name):
    # Проверяем наличие столбца 'id' перед его удалением
    if 'id' in df.columns:
        df_filtered = df.drop(columns=['id'])
    else:
        df_filtered = df  # Если столбца 'id' нет, используем оригинальный DataFrame

    plt.figure(figsize=(10, 6))
    plt.boxplot([df_filtered[col] for col in df_filtered.columns], vert=False)
    plt.title(title_name)  # Заголовок
    plt.xlabel('Значения')  # Подпись оси X
    plt.ylabel('Столбцы')  # Подпись оси Y
    plt.yticks(ticks=np.arange(1, len(df_filtered.columns) + 1), labels=df_filtered.columns)  # Подписи по оси Y
    return plt


def detect_outliers_iqr(df):
    outlier_summary = {}

    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        # Вычисление квартилей
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        # Вычисление границ для выбросов
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Определение выбросов
        lower_outliers = df[df[column] < lower_bound]
        upper_outliers = df[df[column] > upper_bound]
        normal_data = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

        # Заполнение словаря резюме
        outlier_summary[column] = {
            'left_outliers': lower_outliers.shape[0],
            'normal_data': normal_data.shape[0],
            'right_outliers': upper_outliers.shape[0]
        }

    # Конвертация словаря в DataFrame
    summary_df = pd.DataFrame(outlier_summary).T
    summary_df.columns = ['Количество выбросов слева', 'Количество нормальных данных', 'Количество выбросов справа']

    # Фильтрация: оставляем только колонки с выбросами
    summary_df_filtered = summary_df[(summary_df['Количество выбросов слева'] > 0) | 
                                      (summary_df['Количество выбросов справа'] > 0)]

    return summary_df_filtered
   