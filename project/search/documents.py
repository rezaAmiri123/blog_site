from django_elasticsearch_dsl import DocType, Index, fields
from blog.models import Post, User


# Name of the Elasticsearch index
search_index = Index('blog')
# see Elasticsearch Indices API reference for available settings
search_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@search_index.doc_type
class PostDocument(DocType):
    author = fields.NestedField(properties={
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
        'username': fields.TextField(),
        'pk': fields.IntegerField(),
    }, include_in_root=True)

    class Meta:
        model = Post # The model associated with this DocType

        # The fields of the you want to be indexed in Elasticsearch
        fields = [
            'title',
            'body',
            'created'
        ]
        related_models = [User]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Post instance(s) from the related model."""
        if isinstance(related_instance, User):
            return related_instance.blog_posts.all()
