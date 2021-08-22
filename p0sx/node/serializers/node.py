from rest_framework import serializers
from node.models import NodePrintJob, Node


class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = '__all__'


class NodePrintJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodePrintJob
        fields = '__all__'

    receipt_content = serializers.SerializerMethodField()

    def get_receipt_content(self, obj):
        return obj.receipt.content