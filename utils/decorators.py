def helper(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        finally:
            await self.client.session.close()
    return wrapper
