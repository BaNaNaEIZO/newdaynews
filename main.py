from pars import RamblerPars, data_input, choice_day, work_with_os
from correlation import Correlation

# from sys import argv

# prog_name, days, pages, weeks = argv


if __name__ == '__main__':
    work_with_os()
    days, pages, weeks = data_input()
    parser = RamblerPars(days=int(days), pages=int(pages), start_day=choice_day())
    parser.page_request()
    correlation = Correlation(k=int(weeks))
    correlation.all_news_to_excel()
    correlation.all_percent_news_to_excel()
    correlation.all_dependency_news_to_excel()
    correlation.correlation()
