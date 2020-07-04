import os
import uuid
import logging
import seaborn as sns
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('plotManager.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Plot:
    def __init__(self):
        pass

    def bar_plot(self, date, data, x_label, y_label, title, session_id):
        plt.figure(figsize=(18, 10))
        ax = sns.barplot(x=date, y=data)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        ax.set_xlabel(x_label, fontsize=15)
        ax.set_ylabel(y_label, fontsize=15)
        ax.set_title(title, fontsize=15)
        base_dir = 'static/images'
        directory = session_id
        path = os.path.join(base_dir, directory)
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)
            logger.exception("Folder already exists.")

        filename = str(uuid.uuid4().hex)
        file_path = path + "/" + filename + ".png"
        ax.figure.savefig(file_path)
        plt.close('all')
        logger.info(title + " bar chart generated SUCCESSFULLY")
        return file_path

    def donut_chart(self, data, labels, title, session_id):
        explode = (0, 0.1, 0)
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        ax.pie(data, explode=explode, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, pctdistance=0.85,
               shadow=True)

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(title, pad=30)
        base_dir = 'static/images'
        directory = session_id
        path = os.path.join(base_dir, directory)
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)
            logger.exception("Folder already exists.")
        filename = str(uuid.uuid4().hex)
        file_path = path+"/"+filename+".png"
        ax.figure.savefig(file_path)
        plt.close('all')
        logger.info(title + " donut chart generated SUCCESSFULLY")
        return file_path
