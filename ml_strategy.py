from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

class MLStrategy:
    def __init__(self, model_path='ml_model.pkl'):
        self.model_path = model_path
        try:
            self.model = joblib.load(model_path)
        except:
            self.model = RandomForestClassifier()
        self.scaler = StandardScaler()

    def prepare_data(self, df):
        features = ['open', 'high', 'low', 'close', 'volume', 'sma', 'ema', 'rsi', 'macd', 'bb_upper', 'bb_lower']
        X = df[features].fillna(0)
        y = np.where(df['close'].shift(-1) > df['close'], 1, 0)
        return X[:-1], y[:-1]

    def fit(self, df):
        X, y = self.prepare_data(df)
        X = self.scaler.fit_transform(X)
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)

    def predict(self, df_row):
        X = df_row[['open','high','low','close','volume','sma','ema','rsi','macd','bb_upper','bb_lower']].fillna(0)
        X = self.scaler.transform([X.values])
        return self.model.predict_proba(X)[0]
