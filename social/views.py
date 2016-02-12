from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from social.models import Member, Profile, Message, Friends, FriendRequests

appname = 'Facemagazine'

# decorator that tests whether user is logged in
def loggedin(f):
    def test(request):
        if 'username' in request.session:
            return f(request)
        else:
            template = loader.get_template('social/not-logged-in.html')
            context = RequestContext(request, {})
            return HttpResponse(template.render(context))
    return test

def index(request):
    template = loader.get_template('social/index.html')
    context = RequestContext(request, {
    		'appname': appname,
    	})
    return HttpResponse(template.render(context))

def signup(request):
    template = loader.get_template('social/signup.html')
    context = RequestContext(request, {
    		'appname': appname,
    	})
    return HttpResponse(template.render(context))

def register(request):
    u = request.POST['user']
    p = request.POST['pass']
    user = Member(username=u, password=p)
    user.save()
    template = loader.get_template('social/user-registered.html')
    context = RequestContext(request, {
        'appname': appname,
        'username' : u
        })
    return HttpResponse(template.render(context))

def login(request):
    if 'username' not in request.POST:
        template = loader.get_template('social/login.html')
        context = RequestContext(request, {
                'appname': appname,
            })
        return HttpResponse(template.render(context))
    else:
        u = request.POST['username']
        p = request.POST['password']
        try:
            member = Member.objects.get(pk=u)
        except Member.DoesNotExist:
            raise Http404("User does not exist")
        if p == member.password:
            request.session['username'] = u;
            request.session['password'] = p;
            return render(request, 'social/login.html', {
                'appname': appname,
                'username': u,
                'loggedin': True}
                )
        else:
            return HttpResponse("Wrong password")

@loggedin
def friends(request):
    username = request.session['username']
    member_obj = Member.objects.get(pk=username)
    # list of people I'm following
    following = member_obj.following.all()
    # list of people that are following me
    followers = Member.objects.filter(following__username=username)
    # render reponse
    return render(request, 'social/friends.html', {
        'appname': appname,
        'username': username,
        'members': members,
        'following': following,
        'followers': followers,
        'loggedin': True}
        )

@loggedin
def logout(request):
    if 'username' in request.session:
        u = request.session['username']
        request.session.flush()
        template = loader.get_template('social/logout.html')
        context = RequestContext(request, {
                'appname': appname,
                'username': u
            })
        return HttpResponse(template.render(context))
    else:
        raise Http404("Can't logout, you are not logged in")

def member(request, view_user):
    username = request.session['username']
    member = Member.objects.get(pk=view_user)

    if view_user == username:
        greeting = "Your"
    else:
        greeting = view_user + "'s"

    if member.profile:
        text = member.profile.text
    else:
        text = ""
    return render(request, 'social/member.html', {
        'appname': appname,
        'username': username,
        'view_user': view_user,
        'greeting': greeting,
        'profile': text,
        'loggedin': True}
        )

@loggedin
def members(request):
    username = request.session['username']
    member_obj = Member.objects.get(pk=username)

    #Get list of all friends
    allFriends = Friends.objects.all().filter(friend1 = member_obj)

    #Get list of all Members
    allMembers = Member.objects.all().filter()

    # Go through all the friends and remove any duplicates - add more info here
    for friend in allFriends:
        allMembers = allMembers.exclude(pk = friend.friend2)

    allMembers = allMembers.exclude(pk=username)

    #Get list of pending friend requests
    pendingRequests = FriendRequests.objects.all().filter(recipient = member_obj, status = False)

    #Change below variable name
    allFriends2 = allFriends

    #Suggested Friends
    suggestedFriends = []

    for friend in allFriends2:
        friendsFriends = Friends.objects.all().filter(friend1 = friend.friend2)
        friendsFriends = friendsFriends.exclude(friend2 = member_obj)
        #suggestedFriends.append(friendsFriends)
        for friendsFriend in friendsFriends:
            suggestedFriends.append(friendsFriend)

    # send a friend request
    if 'sendFriendRequest' in request.GET:
        friend = request.GET['sendFriendRequest']
        friend_obj = Member.objects.get(pk=friend)
        #Check if a friend request has allready been sent
        if(FriendRequests.objects.all().filter(sender = member_obj, recipient = friend_obj, status = False).count() == 0):
            FriendRequests(sender = member_obj, recipient = friend_obj, status = False).save()

    # Approve a Friend Request
    if 'approveFriendRequest' in request.GET:
        friend = request.GET['approveFriendRequest']
        friend_obj = Member.objects.get(pk=friend)
        #Check if they are friends allready
        if(Friends.objects.all().filter(friend1 = member_obj, friend2 = friend_obj).count() == 0):
            req_obj = FriendRequests.objects.get(sender = friend_obj, recipient = member_obj)
            req_obj.status = True
            req_obj.save()
            Friends(friend1 = member_obj, friend2 = friend_obj).save()
            Friends(friend2 = member_obj, friend1 = friend_obj).save()

    # view user profile
    if 'view' in request.GET:
        return member(request, request.GET['view'])
    else:
        # render reponse
        return render(request, 'social/members.html', {
            'appname': appname,
            'username': username,
            'allFriends': allFriends,
            'allMembers': allMembers,
            'pendingRequests': pendingRequests,
            'suggestedFriends': suggestedFriends,
            'loggedin': True}
            )

@loggedin
def profile(request):
    u = request.session['username']
    member = Member.objects.get(pk=u)
    if 'text' in request.POST:
        text = request.POST['text']
        if member.profile:
            member.profile.text = text
            member.profile.save()
        else:
            profile = Profile(text=text)
            profile.save()
            member.profile = profile
        member.save()
    else:
        if member.profile:
            text = member.profile.text
        else:
            text = ""
    return render(request, 'social/profile.html', {
        'appname': appname,
        'username': u,
        'text' : text,
        'loggedin': True}
        )

@loggedin
def messages(request):
    username = request.session['username']
    user = Member.objects.get(pk=username)
    # Whose message's are we viewing?
    if 'view' in request.GET:
        view = request.GET['view']
    else:
        view = username
    recip = Member.objects.get(pk=view)
    # If message was deleted
    if 'erase' in request.GET:
        msg_id = request.GET['erase']
        Message.objects.get(id=msg_id).delete()
    # If text was posted then save on DB
    if 'text' in request.POST:
        text = request.POST['text']
        pm = request.POST['pm'] == "0"
        message = Message(user=user,recip=recip,pm=pm,time=timezone.now(),text=text)
        message.save()
    messages = Message.objects.filter(recip=recip)
    profile_obj = Member.objects.get(pk=view).profile
    profile = profile_obj.text if profile_obj else ""
    return render(request, 'social/messages.html', {
        'appname': appname,
        'username': username,
        'profile': profile,
        'view': view,
        'messages': messages,
        'loggedin': True}
        )

def checkuser(request):
    if 'user' in request.POST:
        u = request.POST['user']
        try:
            member = Member.objects.get(pk=u)
        except Member.DoesNotExist:
            member = None
        if member is not None:
            return HttpResponse("<span class='taken'>&#x2718;</span>")
        else:
            return HttpResponse("<span class='available'>&#x2714;</span>")

def searchStatus(request):
    #Get all members
    allMembers = Member.objects.all().filter()
    statuss = []

    if request.method == "GET":
        search_text = request.GET['search_text']

    for currentMember in allMembers:
        if search_text in currentMember.username:
            statuss.append(currentMember.username)

    #statuss = search_text

    return render(request, 'social/test.html', {'statuss':statuss})
