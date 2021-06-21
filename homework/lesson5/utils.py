import numpy as np
import pandas as pd


def prefilter_items(data, take_n_popular=None, item_features=None):
    # Подсчет значений для фильтрации
    popularity = (data.groupby('item_id')['user_id'].nunique() / data['user_id'].nunique()).reset_index()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)    
    
    last_week_no = np.sort(data['week_no'].unique())[-1]
    
    prices = data[['item_id']]
    prices['price'] = data['sales_value'] / data['quantity']
    prices = prices.groupby('item_id')['price'].mean().reset_index()
    price_quant_05 = prices['price'].quantile(0.05)
    price_quant_95 = prices['price'].quantile(0.95)
    
    if item_features is not None:
        department_size = pd.DataFrame(item_features. \
                                       groupby('department')['item_id'].nunique(). \
                                       sort_values(ascending=False)).reset_index()

        department_size.columns = ['department', 'n_items']
        rare_departments = department_size[department_size['n_items'] < 150].department.tolist()
    
    # Уберем самые популярные товары (их и так купят)
    top_popular = popularity[popularity['share_unique_users'] > 0.5]['item_id'].unique()
    data = data[~data['item_id'].isin(top_popular)]
    
    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.01]['item_id'].unique()
    data = data[~data['item_id'].isin(top_notpopular)]
    
    # Уберем товары, которые не продавались за последние 12 месяцев
    sold_this_year = data[data['week_no'] > (last_week_no - 52)]['item_id'].unique()
    data = data[data['item_id'].isin(sold_this_year)]
    
    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб. 
    cheap_items = prices.loc[prices['price'] < price_quant_05]['item_id'].unique()
    data = data[~data['item_id'].isin(cheap_items)]
    
    # Уберем слишком дорогие товарыs
    expensive_items = prices.loc[prices['price'] > price_quant_95]['item_id'].unique()
    data = data[~data['item_id'].isin(expensive_items)]
    
    if item_features is not None:
        items_in_rare_departments = item_features[
            item_features['department'].isin(rare_departments)].item_id.unique().tolist()

        data = data[~data['item_id'].isin(items_in_rare_departments)]
    
    # Возьмем только топ 5000 популярных товаров из оставшихся
    if take_n_popular is not None:
        items_sold = data.groupby('item_id')['quantity'].sum().reset_index()
        top_5000 = items_sold.sort_values('quantity', ascending=False).iloc[:take_n_popular]['item_id'].unique()
        data.loc[~data['item_id'].isin(top_5000), 'item_id'] = 999999
    
    return data
    
    
def postfilter_items(user_id, recommednations):
    pass
