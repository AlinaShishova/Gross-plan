
import pandas as pd
import plotly.express as px

def generate_heatmap():
    """Генерирует интерактивную heatmap загрузки ресурсов."""
    # Пример данных (можно заменить на загрузку из БД/API)
    data = {
        "Ресурс": ["Станок 1", "Станок 2", "Бригада 1", "Бригада 2"],
        "Пн": [85, 90, 110, 75],
        "Вт": [95, 80, 105, 70],
        "Ср": [100, 75, 115, 80],
        "Чт": [90, 85, 95, 90],
        "Пт": [80, 70, 100, 85],
        "Сб": [65, 60, 75, 50],
        "Вс": [50, 40, 30, 20]
    }
    df = pd.DataFrame(data).set_index("Ресурс")

    # Создание heatmap
    fig = px.imshow(
        df,
        labels=dict(x="День недели", y="Ресурс", color="Загрузка (%)"),
        color_continuous_scale="RdYlGn_r",
        range_color=[0, 100],
        zmin=0,
        zmax=100,
        text_auto=True,
        aspect="auto"
    )

    # Настройка макета
    fig.update_layout(
        title="Загрузка производственных ресурсов",
        xaxis_nticks=7,
        yaxis_nticks=4,
        font=dict(size=12)
    )

    return fig.to_html(full_html=False)