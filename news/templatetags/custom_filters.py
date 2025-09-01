from django import template


class FilterException(Exception):
   pass


register = template.Library()


CURRENCIES_SYMBOLS = {
   'rub': 'Р',
   'usd': '$',
}


@register.filter()
def currency(value, code='rub'):
   """
   value: значение, к которому нужно применить фильтр
   code: код валюты
   """
   postfix = CURRENCIES_SYMBOLS[code]

   return f'{value} {postfix}'


OBSCENE_WORDS = ['объем', 'развития', "один", "торонто","юниоры"]


@register.filter()
def censor(value):
   if not  isinstance(value, str):
      raise FilterException("Фильтр применяется только к строке")


   for word in OBSCENE_WORDS:
       word_low = word.title()
       value = value.replace(word,word[0]+ '*' * (len(word) - 1))
       value = value.replace(word_low, word_low[0] + '*' * (len(word) - 1))
   return value

@register.filter
def is_string(value):
    """Возвращает True, если значение является строкой"""
    return isinstance(value, str)


