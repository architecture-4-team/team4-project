#include <Windows.h>
#include "ContactManager.h"
#include <iostream>
#include <gst/gst.h>

// creator
ContactManager::ContactManager() {
	g_print("create contact manager");
}

// destroyer
ContactManager::~ContactManager() {
}

bool ContactManager::doSomething()
{
	g_print("dododo");
	return true;
}


