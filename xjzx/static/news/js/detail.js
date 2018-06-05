function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    vue_list_con = new Vue({
        el: '.comment_list_con',
        delimiters: ['[[', ']]'],
        data: {
            comment_list: []
        }
    });
    get_comment_list();
    // 收藏
    $(".collection").click(function () {
        $.post('/collect', {
            'news_id': $('#news_id').val(),
            'csrf_token': $('#csrf_token').val()
        }, function (data) {
            if (data.result == 1) {
                $('.login_btn').click();
            }
            else if (data.result == 5) {
                $('.collection').hide();
                $('.collected').show();
            }
        })

    });

    // 取消收藏
    $(".collected").click(function () {
        $.post('/collect', {
            'news_id': $('#news_id').val(),
            'csrf_token': $('#csrf_token').val(),
            'flag': 2
        }, function (data) {
            if (data.result == 5) {
                $('.collection').show();
                $('.collected').hide();
            }

        });

    });

    // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var msg = $('#msg').val();
        if (msg.length <= 0) {
            alert('评论内容不能为空');
            return;
        }

        $.post('/comment/add', {
            'news_id': $('#news_id').val(),
            'msg': msg,
            'csrf_token': $('#csrf_token').val()
        }, function (data) {
            if (data.result == 1) {
                $('#msg').val('');
                get_comment_list();
                $('.comment').text(data.comment_count);
                $('.comment_count>span').text(data.comment_count);

            }

        });


    });

    $('.comment_list_con').delegate('a,input', 'click', function () {

        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);
            var action = 1;
            var commentid = $this.attr('commentid');
            if (sHandler.indexOf('has_comment_up') >= 0) {
                action = 2;
            }
            $.post('/comment/up/' + commentid, {
                'csrf_token': $('#csrf_token').val(),
                'action': action
            }, function (data) {
                if (data.result == 1) {
                    $('.login_btn').click();
                } else if (data.result == 2) {
                    $this.text(data.like_count);
                    if (action == 1) {
                        $this.addClass('has_comment_up');
                    }
                    else {
                        $this.removeClass('has_comment_up');
                    }

                }

            });

        }

        if (sHandler.indexOf('reply_sub') >= 0) {
            $this=$(this);

            $.post('/comment/back',{
                'news_id':$('#news_id').val(),
                'comment_id':$this.attr('commentid'),
                'msg':$this.prev().val(),
                'csrf_token':$('#csrf_token').val()
            },function (data) {
                if(data.result==1){
                    alert('请填写回复内容');
                }
                else if (data.result==2){
                    $('.login_btn').click();
                } else if (data.result==3){
                    get_comment_list();
                    $this.prev().val("");
                    $this.parent().hide();
                }
            });
        }
    });

    // 关注当前新闻作者
    $(".focus").click(function () {
        $.post('/follow',{
            'csrf_token':$('#csrf_token').val(),
            'follow_user_id':$('#user_id').val(),  // 这篇文章作者的id
            'action':1
        },function (data) {
            if (data.result ==2){
                $('.login_btn').click();
            } else if (data.result == 3){
                $('.focus').hide();
                $('.focused').show();
                $('.follows>b').text(data.follow_count);
            }
        });
    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        $.post('/follow',{
            'csrf_token': $('#csrf_token').val(),
            'follow_user_id':$('#user_id').val(),
            'action':2
        },function (data) {
            if(data.result==2){
                $('.login_btn').click();
            } else if (data.result ==3){
                $('.focus').show();
                $('.focused').hide();
                $('.follows>b').text(data.follow_count);
            }
        })
    });
});

function get_comment_list() {
    $.get('/comment/list/' + $('#news_id').val(), function (data) {
        vue_list_con.comment_list = data.comment_list;
    })
}