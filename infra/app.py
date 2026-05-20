import aws_cdk as cdk
from stack import MiMercadoStack

app = cdk.App()
MiMercadoStack(app, 'MiMercadoStack',
    env=cdk.Environment(account='000000000000', region='us-east-1'),
)
app.synth()
