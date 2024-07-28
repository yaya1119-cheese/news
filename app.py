from flask import Flask, jsonify, request

app = Flask(__name__)

# Global variable to store posts and comments 
posts = {
    0: {
        "id": 0,
        "upvotes": 8,
        "title": "My dog with 2 balls in his mouth",
        "link": "https://imgur.com/gallery/im-18-624-points-from-glorious-so-heres-picture-of-dog-with-two-his-mouth-XgbZdeA",
        "username": "user98",

    }
}

comments = {
    0:{
        "id": 0,
        "post_id": 0, 
        "upvotes": 8,
        "text": "Thanks for my first Reddit gold!",
        "username": "user98",
        }
}

comment_id_counter = 1
post_id_counter = 1


## POST ROUTES ## 

@app.route("/api/posts/", methods=["GET"])
def get_all_posts():
    # Return list of all posts present
    posts_list = []
    for post in posts.values():
        post_data = {
            'id': post['id'],
            'upvotes': post['upvotes'],
            'title': post['title'],
            'link': post['link'],
            'username': post['username'],
        }
        posts_list.append(post_data)
    
    return jsonify({"posts": posts_list}), 200


@app.route("/api/posts/ordered", methods=["GET"])
def get_all_posts_ordered():


    ordering = request.args.get("ordering", "dec")

    parameter_list = ["dec", "inc"]
    if ordering not in parameter_list:
        return jsonify({"error": "invalid "}), 400
    
    post_list = list(posts.values())

    def sort_value_post(post):
        return post['upvotes']
    
    if ordering == "dec":
        post_list.sort(key=sort_value_post, reverse=True)
    else:
        post_list.sort(key=sort_value_post)

    return jsonify(post_list), 200





@app.route("/api/posts/", methods=["POST"])
def create_post():
    # Create a new post using the data provided
    global post_id_counter

    # get data from request body
    data = request.json

    # check the fields in data (should have title)
    field_list = ["title", "link", "username"]
    if not all(key in data for key in field_list):
        return jsonify({"error": "Missing fields in request"}), 400
    
    # TODO: validate link value here

    # new post
    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": data["title"],
        "link": data["link"],
        "username": data["username"],
    }
    
    # add new post to our dictionary (aka db)
    posts[post_id_counter] = post
    post_id_counter += 1
    
    return jsonify(post), 201


@app.route("/api/posts/<int:id>/", methods=["GET"])
def get_post(id):
    # Returns the post with given id
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404
    
    post = posts[id]
    post_data = {
        "id": post['id'],
        "upvotes": post['upvotes'],
        "title": post["title"],
        "link": post["link"],
        "username": post["username"],
    }
    
    return jsonify(post_data), 200


@app.route("/api/posts/<int:id>/", methods=["DELETE"])
def delete_post(id):
    # Delete post with given id
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404
    post = posts.pop(id)
    post_data = {
        "id": post['id'],
        "upvotes": post['upvotes'],
        "title": post["title"],
        "link": post["link"],
        "username": post["username"],
    }
    
    # TODO: also delete the comments below 
    return jsonify(post_data), 200


@app.route("/api/posts/<int:id>/upvote/", methods=["POST"])
def upvote_post(id):
    # Increment upvotes on a specific post (default +1)
    if id not in posts:
       return jsonify({"error": "Post not found"}), 404
    
    upvote_offset = 1 # default
    if request.data:
        # request body provided
        data = request.json
        field_list = ["upvotes"]
        if not all(key in data for key in field_list):
            return jsonify({"error": "Missing fields in request"}), 400
        # validate request body value
        if not isinstance(data['upvotes'], int) or data['upvotes'] < 1:
            return jsonify({"error": "Invalid value in request"}), 400
        
        upvote_offset = data['upvotes']
    
    post = posts[id]
    post['upvotes'] += upvote_offset 

    post_data = {
        "id": post['id'],
        "upvotes": post['upvotes'],
        "title": post["title"],
        "link": post["link"],
        "username": post["username"],
    }

    return jsonify(post_data), 200


## COMMENT ROUTES ##
 
@app.route("/api/posts/<int:id>/comments/", methods=["GET"])
def get_comments(id):
        # Return list of all posts present
    comments_list = []
    for comment in comments.values():
        if comment['post_id'] == id:
            #copy of comment without post_id

            comment_data = {
                'id': comment['id'],
                'upvotes': comment['upvotes'],
                'text': comment['text'],
                'username': comment['username'],
            }
            comments_list.append(comment_data)
    
    return jsonify({"comments": comments_list}), 200
 

@app.route("/api/posts/<int:id>/comments/", methods=["POST"])
def create_comment(id):

    if id not in posts:
        return jsonify({"error": "Post not found"}), 404


    global comment_id_counter

    data = request.json

    field_list = ["text", "username"]
    if not all(key in data for key in field_list):
        return jsonify({"error": "Missing fields in request"}), 400

    
    comment = {

        "id": comment_id_counter,
        "post_id": id,
        "text": data["text"],
        "username": data["username"],
    }


    comments[comment_id_counter] = comment
    comment_id_counter += 1

    return jsonify(comment), 201
    

@app.route("/api/posts/<int:pid>/comments/<int:cid>/", methods=["POST"])
def edit_comment(pid, cid):

    if pid not in posts:
        return jsonify({"error": "Post not found"}), 404
    if cid not in comments:
        return jsonify({"error": "Comment not found"}), 404
    
    data = request.json

    field_list = ["text"]
    if not all(key in data for key in field_list):
        return jsonify({"error": "Missing fields in request"}), 400
    
    comment = comments[cid]

    if comment["post_id"] != pid:
        return jsonify({"error": "Comment not for this post"}), 400
    
    comment['text'] = data['text']


    comments[cid] = comment


    comment_data = {
        'id': comment['id'],
        'upvotes': comment['upvotes'],
        'text' : comment['text'],
        'username': comment['username'],
    }

    return jsonify(comment_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)                                  