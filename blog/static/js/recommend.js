function refresh(post_id){
        
            console.log(post_id)
            $.ajax({
            type: "GET",
            url: "/recommend/"+post_id,
            data: "",
            success:function(result){
                
                date = JSON.parse(result);
                if(date['登录'])
                {
                    alert('请先登录！');
                }
                else if(date['已推荐'] == '-1')
                    alert('您已推荐过!');
                else
                    {
                        var spanid = "#span"+post_id;
                        $(spanid).html(date['count']);
                        alert('推荐成功!');
                    }
            }
        });
        }