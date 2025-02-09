import pandas as pd
import numpy as np
import math


class Correlation:
    def __init__(self, input_file="files/news.csv", output_file="files/output.xlsx", encoding="utf-8", k=5):
        self.input = input_file
        self.output = output_file
        self.encoding = encoding
        self.k = k

    def load_file(self):
        # Загрузка данных в датафрейм
        df = pd.read_csv(self.input)
        # df = df.drop([i for i in range(len(df["tag"].unique()))])  # Костыль закрыает 53 неделю, которой нет в 2023 году
        return df

    def dataframe_transform_to_correlation(self):
        # Загрузка датафрейма
        df = self.load_file()
        # Параметры стобца week
        list_of_week = [item for item in df["week"].unique()]
        all_week_lenght = len(list_of_week)
        # Параметры столбца tag
        list_of_tag = [item for item in df["tag"].unique()]
        all_tag_lenght = len(list_of_tag)
        # Создаем массив для заполнения нового датафрейма
        data = df["sum_news"].tolist()
        data = np.reshape(data, (all_week_lenght, all_tag_lenght))
        data = np.transpose(data)
        # Создание нового датафрейма на основе старых данных
        df2 = pd.DataFrame(data, columns=list_of_week, index=list_of_tag)
        df2 = df2.transpose()
        return df2, list_of_week, list_of_tag

    def correlation(self):
        list_current_week = []
        sums = []
        row_sum = []
        # Файл output.xlsx
        with pd.ExcelWriter(self.output, engine='xlsxwriter') as writer:
            df, list_of_week, list_of_tag = self.dataframe_transform_to_correlation()  #
            len_lag = len(list_of_week) - self.k + 1
            for i in range(len_lag):
                df_corr = df.iloc[i:self.k + i, :]

                for item in df_corr.index:
                    list_current_week.append(item)
                df_corr = df_corr.corr()
                self.sum_dataframe(df_corr)
                sums.append(self.sum_dataframe(df_corr))
                row_sum.append("week" + str(list_current_week))
                list_of_all_sums_pos, list_of_all_sums_neg = self.sum_corr(df_corr)
                all_character, character, flag = self.sum_of_characters(df_corr)
                list_all_character = []
                list_all_character = all_character + [np.nan] * (len(df_corr.index) - len(all_character))
                sums[i] = sums[i] + (list_all_character[0], list_all_character[1], list_all_character[2],)
                df_sum = pd.DataFrame(sums, index=row_sum,
                                      columns=["positive", "negative", "abs", "konf +", "konf -", "konf"])

                # Добавляет к output строки снизу
                df_corr.loc[" "] = np.nan
                df_corr.loc["Конфликт"] = flag
                df_corr.loc["+/-"] = character
                df_corr.loc["Сумма +/-"] = list_all_character
                df_corr.loc[" "] = np.nan
                df_corr.loc["Положительные"] = list_of_all_sums_pos
                df_corr.loc["Отрицательные"] = list_of_all_sums_neg

                df_corr.to_excel(writer, sheet_name=f'week{list_current_week[0]}-{list_current_week[-1]}',
                                 index=True)
                list_current_week = []
                if len_lag - 1 == i:
                    df_sum.to_excel(writer, sheet_name=f'Итоговый график')

    def sum_corr(self, df):
        list_of_all_sums_pos = []
        list_of_all_sums_neg = []
        for item in df.columns:
            list_df = df[item].fillna(0).tolist()

            if sum(list_df) != 0:
                sum_pos = -1
            else:
                sum_pos = 0
            sum_neg = 0

            for i in list_df:
                if i >= 0:
                    sum_pos += i
                elif i < 0:
                    sum_neg += i
            list_of_all_sums_pos.append(sum_pos)
            list_of_all_sums_neg.append(sum_neg)
        return list_of_all_sums_pos, list_of_all_sums_neg

    def sum_of_characters(self, df):
        list_flag = []
        list_flag_all = []
        list_sum_characters = []
        list_all_sum_pos_characters = 0
        list_all_sum_neg_characters = 0
        all_character = [0, 0, ""]
        # Преобразовываем df в list и проходимся по столбцам
        for item in df.columns:
            list_df = df[item].tolist()
            new_list_df = []
            # Убираем 0 и nan из столбца матрицы корреляции
            for i in list_df:
                if not ((math.isclose(i, 0.0)) or math.isnan(i)):
                    new_list_df.append(i)

            len_list_df = 0

            if len(new_list_df) >= 1:
                len_list_df = len(new_list_df) - 1  # Вычисляем количество значимых чисел в столбце матрицы
                sum_characters = np.sum(np.array(new_list_df) > 0, axis=0) - 1  # Вычисляем сумму положительных чисел
                sum_minus = len_list_df - sum_characters
            else:
                len_list_df = 0
                sum_characters = 0
                sum_minus = 0

            list_sum_characters.append(  #
                f"+{sum_characters} -{sum_minus}")  # Формируем запись о знаках в столбце таблицы

            # Список всех положительных знаков в рамках одной матрицы
            list_all_sum_pos_characters += sum_characters
            # Список всех отрицательных знаков в рамках одной матрицы
            list_all_sum_neg_characters += len_list_df - sum_characters

            # Проверка конфликтов по столбцам v2
            if sum_characters > sum_minus or sum_characters == sum_minus or (
                    (sum_minus - sum_characters) > 0) and (sum_minus - sum_characters) % 2 == 0:
                list_flag.append("нет")
            else:
                list_flag.append("ЕСТЬ")  # Какая-то ошибка

            # # Проверка конфликтов по столбцам
            # if (((len_list_df - sum_characters) % 2 == 0) or (len_list_df == sum_characters)) or (
            #         (len_list_df - sum_characters) == sum_characters) and (
            #         (len_list_df - sum_characters) < sum_characters):
            #     list_flag.append("нет")
            # elif (len_list_df - sum_characters) > sum_characters or ((len_list_df - sum_characters) % 2) == 1:
            #     list_flag.append("ЕСТЬ")
            # else:
            #     list_flag.append("Не понятно")  # Какая-то ошибка

        # Проверка конфликта у всей матрицы
        # if (((list_all_sum_neg_characters % 2 == 0) or (
        #         list_all_sum_pos_characters == list_all_sum_pos_characters + list_all_sum_neg_characters)) or (
        #             list_all_sum_pos_characters == list_all_sum_neg_characters)) and (
        #         list_all_sum_neg_characters < list_all_sum_pos_characters):
        #     list_flag_all.append("нет")
        # elif list_all_sum_neg_characters > list_all_sum_pos_characters or (list_all_sum_neg_characters % 2) == 1:
        #     list_flag_all.append("ЕСТЬ")
        # else:
        #     list_flag_all.append("Не понятно")

        # Проверка конфликта у всей матрицы v2
        if list_all_sum_pos_characters > list_all_sum_neg_characters or list_all_sum_pos_characters == list_all_sum_neg_characters or (
                (list_all_sum_neg_characters - list_all_sum_pos_characters) > 0) and (
                list_all_sum_neg_characters - list_all_sum_pos_characters) % 2 == 0:
            list_flag_all.append("нет")
        else:
            list_flag_all.append("ЕСТЬ")  # Какая-то ошибка

        # Формирование вывода сумм знаков и конфликта для всей матрицы
        all_character[0] = f"+{list_all_sum_pos_characters}"
        all_character[1] = f"-{list_all_sum_neg_characters}"
        all_character[2] = f"{list_flag_all[0]}"

        # Для вей матрицы, список суммы +/- по столбцам, конфликтность для столбцов
        return all_character, list_sum_characters, list_flag

    def all_news_to_excel(self):
        df = pd.read_csv("files/news.csv")
        sps_weeks = df.week.tolist()[::45]
        sps_tag_len = len(list(set(df.tag.tolist())))
        sps_tags = df.tag.tolist()[:sps_tag_len]
        sps_sum_news = df.sum_news.tolist()
        # sps_weeks.sort(reverse=True)

        list_news = []
        count_of_news_start = 0
        count_of_news_end = len(sps_tags)
        for week in sps_weeks:
            temp_dict = {}
            temp_list = sps_sum_news[count_of_news_start:count_of_news_end]
            i = 0
            for tag in sps_tags:
                temp_dict[tag] = temp_list[i]
                i += 1
            list_news.append(temp_dict)

            count_of_news_end += len(sps_tags)
            count_of_news_start += len(sps_tags)
        column = sps_weeks.copy()
        column.sort()
        df = pd.DataFrame(list_news, index=sps_weeks).T
        df = df.reindex(column, axis="columns")
        df.to_excel("files/all_news.xlsx")

    def all_dependency_news_to_excel(self):
        df = pd.read_csv("files/news.csv")
        sps_weeks = df.week.tolist()[::45]
        sps_tag_len = len(list(set(df.tag.tolist())))
        sps_tags = df.tag.tolist()[:sps_tag_len]
        sps_sum_news = df.sum_news.tolist()
        # sps_weeks.sort(reverse=True)

        count_of_news_start = 0
        count_of_news_end = len(sps_tags)
        with pd.ExcelWriter("files/all_dependency_news.xlsx") as writer:
            for week in sps_weeks:
                list_news = []
                temp_dict_percent = {}
                temp_dict_abs = {}
                temp_list = sps_sum_news[count_of_news_start:count_of_news_end]
                i = 0
                for tag in sps_tags:
                    if sum(temp_list) != 0:
                        temp_dict_percent[tag] = round(temp_list[i] / max(temp_list) * 100, 1)
                    else:
                        temp_dict_percent[tag] = 0
                    temp_dict_abs[tag] = temp_list[i]
                    i += 1
                list_news.append(temp_dict_percent)
                list_news.append(temp_dict_abs)
                df = pd.DataFrame(list_news).T
                df.to_excel(writer, sheet_name=f"week_{week}")
                count_of_news_end += len(sps_tags)
                count_of_news_start += len(sps_tags)

    def all_percent_news_to_excel(self):
        df = pd.read_csv("files/news.csv")
        sps_weeks = df.week.tolist()[::45]
        sps_tag_len = len(list(set(df.tag.tolist())))
        sps_tags = df.tag.tolist()[:sps_tag_len]
        sps_sum_news = df.sum_news.tolist()
        # sps_weeks.sort(reverse=True)

        count_of_news_start = 0
        count_of_news_end = len(sps_tags)
        with pd.ExcelWriter("files/all_percent_news.xlsx") as writer:
            for week in sps_weeks:
                list_news = []
                temp_dict_percent = {}
                temp_dict_abs = {}
                temp_list = sps_sum_news[count_of_news_start:count_of_news_end]
                i = 0
                for tag in sps_tags:
                    if sum(temp_list) != 0:
                        temp_dict_percent[tag] = round(temp_list[i] / sum(temp_list) * 100, 1)
                    else:
                        temp_dict_percent[tag] = 0
                    temp_dict_abs[tag] = temp_list[i]
                    i += 1
                list_news.append(temp_dict_percent)
                list_news.append(temp_dict_abs)
                df = pd.DataFrame(list_news).T
                df.to_excel(writer, sheet_name=f"week_{week}")
                count_of_news_end += len(sps_tags)
                count_of_news_start += len(sps_tags)

    def sum_dataframe(self, df):
        list_of_all_sums_pos = []
        list_of_all_sums_neg = []
        for item in df.columns:
            list_df = df[item].fillna(0).tolist()

            if sum(list_df) != 0:
                sum_pos = -1
            else:
                sum_pos = 0
            sum_neg = 0

            for i in list_df:
                if i >= 0:
                    sum_pos += i
                elif i < 0:
                    sum_neg += i
            list_of_all_sums_pos.append(sum_pos)
            list_of_all_sums_neg.append(sum_neg)
        return sum(list_of_all_sums_pos), sum(list_of_all_sums_neg), sum(list_of_all_sums_pos) + abs(
            sum(list_of_all_sums_neg))
