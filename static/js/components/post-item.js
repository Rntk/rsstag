'use strict';
import React from 'react';

export default class PostsItem extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            post: props.post
        };
        this.showed = false;
        this.clickReadButton = this.clickReadButton.bind(this);
        this.showPostLinks = this.showPostLinks.bind(this);
        this.changePostsContentState = this.changePostsContentState.bind(this);
        this.setCurrent = this.setCurrent.bind(this);
        this.getNode = this.getNode.bind(this);
    }

    setCurrent() {
        this.props.ES.trigger(this.props.ES.SET_CURRENT_POST, this.state.post.pos);
    }

    clickReadButton() {
        this.props.ES.trigger(this.props.ES.CHANGE_POSTS_STATUS,{ids: [this.state.post.pos], readed: !this.state.post.post.read});
    }

    showPostLinks() {
        this.props.ES.trigger(this.props.ES.SHOW_POST_LINKS, this.state.post.pos);
    }

    changePostsContentState() {
        this.props.ES.trigger(this.props.ES.CHANGE_POSTS_CONTENT_STATE, {ids: [this.state.post.pos], showed: !this.state.post.showed});
    }

    componentDidUpdate() {
        if (this.state.post.current && (this.showed !== !!this.state.post.showed)) {
            this.showed = this.state.post.showed;
            window.scrollTo(0, this.node.offsetTop);
            this.need_scroll = false;
        }
    }

    dangerHTML(post) {
        let html = {__html: ''};

        if (post.showed) {//TODO: add content clearing from scripts, iframes etc.
            html = {__html: post.post.content.content};
        }

        return html;
    }

    getNode(node) {
        this.node = node;
    }

    render() {
        if (this.state) {
            let links = '',
                post = this.state.post,
                read_button_class = (post.post.read)? 'read': 'unread';
            if (post.links) {
                let tags = [],
                    grouped_links = {};

                post.links.tags.forEach(tag => {
                    let letter = tag.tag.charAt(0);

                    if (!(letter in grouped_links)) {
                        grouped_links[letter] = [];
                    }
                    grouped_links[letter].push(<a href={tag.url} key={tag.tag} className="post_tag_link"> {tag.tag}</a>)
                });
                for (let letter in grouped_links) {
                    tags.push(
                        <div key={post.pos + letter} className="post_tag_letter_block">
                            <span className="post_tag_letter">{letter}</span>
                            {grouped_links[letter]}
                        </div>
                    )
                }
                links = (
                    <div>
                        <a href={post.links.c_url}>{post.links.c_title}</a>&nbsp;| &nbsp;
                        <a href={post.links.f_url}>{post.links.f_title}</a>&nbsp;| &nbsp;
                        <a href={post.links.p_url}>To site</a><br />
                        {tags}
                    </div>
                );
            }
            return(
                <div className={"post " + (this.state.post.current? "current_post": "")} key={post.pos} ref={this.getNode} onClick={this.setCurrent}><a name={'p' + post.pos}></a>
                    <h3 className="post_title">
                        <a className="post_title_link" href={post.post.url} target="_blank" dangerouslySetInnerHTML={{__html: post.post.content.title}}></a>
                    </h3>
                    <div className="post_meta">
                        #{post.pos} |
                        {post.category_title} |
                        <b className="post_feed_title">{post.feed_title}</b> |
                        {post.post.date}{(post.post.clusters)? ' | ' + post.post.clusters.join(', '): ''}
                    </div>
                    <div className={'post_content ' + post.showed? '': 'hide'} dangerouslySetInnerHTML={this.dangerHTML(post)}></div>
                    <div className="post_tools">
                        <span className="post_show_content" onClick={this.changePostsContentState}>{post.showed? 'Hide': 'Show'} post</span>
                        <span className="post_show_links" onClick={this.showPostLinks}>Show links</span>
                        <span className={'read_button ' + read_button_class} onClick={this.clickReadButton}>{read_button_class}</span>
                        <div className={'post_links_content ' + (post.links? '': 'hide')}>{links}</div>
                    </div>
                </div>
            );
        } else {
            return(<p>No posts</p>);
        }
    }
};