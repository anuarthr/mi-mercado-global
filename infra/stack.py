import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

LAMBDA_ENV = {
    'DYNAMODB_ENDPOINT_URL': 'http://localstack:4566',
    'DYNAMODB_TABLE_NAME':   'mi_mercado',
    'REDIS_URL':             'redis://redis:6379/0',
}


class MiMercadoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Tabla DynamoDB 
        table = dynamodb.Table(
            self, 'MiMercadoTable',
            table_name='mi_mercado',
            partition_key=dynamodb.Attribute(
                name='pk',
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name='sk',
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Empaquetado
        # Las dependencias se instalan previamente con:
        code = _lambda.Code.from_asset('../lambda')

        # Funciones Lambda
        fn_usuarios = _lambda.Function(
            self, 'UsuariosFunction',
            function_name='mi-mercado-usuarios',
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler='usuarios.handler.lambda_handler',
            code=code,
            environment=LAMBDA_ENV,
            timeout=Duration.seconds(30),
        )

        fn_pedidos = _lambda.Function(
            self, 'PedidosFunction',
            function_name='mi-mercado-pedidos',
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler='pedidos.handler.lambda_handler',
            code=code,
            environment=LAMBDA_ENV,
            timeout=Duration.seconds(30),
        )

        fn_items = _lambda.Function(
            self, 'ItemsFunction',
            function_name='mi-mercado-items',
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler='items.handler.lambda_handler',
            code=code,
            environment=LAMBDA_ENV,
            timeout=Duration.seconds(30),
        )

        # Permisos DynamoDB
        table.grant_read_write_data(fn_usuarios)
        table.grant_read_write_data(fn_pedidos)
        table.grant_read_write_data(fn_items)

        # API Gateway
        api = apigw.RestApi(
            self, 'MiMercadoApi',
            rest_api_name='mi-mercado-api',
            description='Mi Mercado Global — Serverless API',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        int_usuarios = apigw.LambdaIntegration(fn_usuarios, proxy=True)
        int_pedidos  = apigw.LambdaIntegration(fn_pedidos,  proxy=True)
        int_items    = apigw.LambdaIntegration(fn_items,    proxy=True)

        # POST /usuarios/
        # GET  /usuarios/{userId}/
        usuarios = api.root.add_resource('usuarios')
        usuarios.add_method('POST', int_usuarios)

        usuario = usuarios.add_resource('{userId}')
        usuario.add_method('GET', int_usuarios)

        # GET /usuarios/{userId}/pedidos/
        usuario_pedidos = usuario.add_resource('pedidos')
        usuario_pedidos.add_method('GET', int_pedidos)

        # POST /pedidos/
        # GET  /pedidos/{pedidoId}/
        pedidos = api.root.add_resource('pedidos')
        pedidos.add_method('POST', int_pedidos)

        pedido = pedidos.add_resource('{pedidoId}')
        pedido.add_method('GET', int_pedidos)

        # GET  /pedidos/{pedidoId}/items/
        # POST /pedidos/{pedidoId}/items/
        items = pedido.add_resource('items')
        items.add_method('GET',  int_items)
        items.add_method('POST', int_items)

        # Outputs
        cdk.CfnOutput(self, 'ApiUrl',
            value=api.url,
            description='URL base del API Gateway en LocalStack',
        )
